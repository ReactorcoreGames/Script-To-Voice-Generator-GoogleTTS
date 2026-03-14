"""
Audio generation orchestration for Script to Voice Generator.
Handles the full pipeline: TTS generation per line, effects processing,
SFX processing, merged audio production, and reference sheet output.
Runs in a background thread with progress callbacks to the GUI.
"""

import threading
import traceback
from pathlib import Path

from audio_generator import AudioGenerator, is_yell_line
from audio_merger import AudioMerger
from config import AUDIO_EFFECTS
from file_manager import FileManager


class GenerationMixin:
    """Mixin class for full audio generation pipeline."""

    def run_generation(self):
        """
        Start the full generation process in a background thread.
        Called from Tab 3's generate button handler after validation.
        """
        if self._gen_running:
            return

        self._gen_running = True
        self._gen_cancel_requested = False

        # Disable generate, enable cancel
        self._btn_generate.config(state="disabled")
        self._btn_cancel.config(state="normal")
        self._btn_open_output.config(state="disabled")

        self.gen_log_clear()
        self.gen_progress(0, "Starting generation...")

        # Gather all settings from the GUI into a plain dict
        # so the background thread doesn't touch tkinter vars directly
        settings = self._gather_generation_settings()

        thread = threading.Thread(target=self._generation_worker, args=(settings,), daemon=True)
        thread.start()

    def _gather_generation_settings(self):
        """Read all GUI state needed for generation into a plain dict."""
        result = self._last_parse_result
        project_name = self._gen_project_name_var.get().strip()
        output_folder = self._gen_output_folder_var.get().strip()

        # Per-speaker settings
        speakers = {}
        for speaker_id in result.speakers:
            vars_dict = self._speaker_vars.get(speaker_id, {})
            if not vars_dict:
                continue

            voice_val = vars_dict["voice"].get()
            if " | " in voice_val:
                voice_name = voice_val.split(" | ")[0]
            else:
                voice_name = voice_val

            pitch_semitones = vars_dict["pitch_semitones"].get()
            speaking_rate = vars_dict["speaking_rate"].get()
            yell_impact = vars_dict["yell_impact_percent"].get()
            volume = vars_dict["volume_percent"].get()

            effects = {}
            for eff_name in AUDIO_EFFECTS:
                effects[eff_name] = vars_dict[eff_name].get()
            effects["fmsu"] = vars_dict["fmsu"].get()
            effects["reverse"] = vars_dict["reverse"].get()

            speakers[speaker_id] = {
                "voice_name": voice_name,
                "pitch_semitones": pitch_semitones,
                "speaking_rate": speaking_rate,
                "yell_impact": yell_impact,
                "volume": volume,
                "effects": effects,
            }

        # SFX settings
        sfx_effects = {}
        for eff_name in AUDIO_EFFECTS:
            var = self._sfx_effect_vars.get(eff_name)
            sfx_effects[eff_name] = var.get() if var else "off"
        sfx_effects["fmsu"] = self._sfx_fmsu_var.get()
        sfx_effects["reverse"] = self._sfx_reverse_var.get()

        # Which SFX files are included
        sfx_included = {}
        for filename, check_var in self._sfx_check_vars.items():
            sfx_included[filename] = check_var.get()

        # SFX resolved paths from parse result
        sfx_paths = {}
        for sfx_event in result.sound_effects:
            if sfx_event.found and sfx_event.found_path:
                sfx_paths[sfx_event.filename] = sfx_event.found_path

        use_project_subfolder = self._gen_use_project_subfolder_var.get()

        # Silence trimming settings (gathered from config_manager, not from tk vars,
        # since the silence trim section in Tab 4 writes directly to config_manager)
        silence_trim_mode = self.config_manager.get_silence_trim("mode") or "beginning_end"

        output_format = self.config_manager.get_output_format()

        return {
            "project_name": project_name,
            "output_folder": output_folder,
            "use_project_subfolder": use_project_subfolder,
            "parse_result": result,
            "speakers": speakers,
            "sfx_effects": sfx_effects,
            "sfx_included": sfx_included,
            "sfx_paths": sfx_paths,
            "config_manager": self.config_manager,
            "silence_trim_mode": silence_trim_mode,
            "output_format": output_format,
        }

    def _generation_worker(self, settings):
        """Background thread: run the full generation pipeline."""
        try:
            self._do_generation(settings)
        except Exception as e:
            tb = traceback.format_exc()
            self.root.after(0, lambda: self._on_generation_error(str(e), tb))

    def _do_generation(self, settings):
        """Core generation logic. Runs in background thread."""
        project_name = settings["project_name"]
        output_folder = Path(settings["output_folder"])
        if settings.get("use_project_subfolder", True):
            output_folder = output_folder / project_name
        result = settings["parse_result"]
        speaker_settings = settings["speakers"]

        output_folder.mkdir(parents=True, exist_ok=True)
        clips_clean_folder = output_folder / "clips_clean"
        clips_effect_folder = output_folder / "clips_effect"
        clips_clean_folder.mkdir(exist_ok=True)
        clips_effect_folder.mkdir(exist_ok=True)

        # Collect dialogue lines for processing
        dialogue_lines = [l for l in result.lines if l.line_type == "dialogue"]
        total_lines = len(dialogue_lines)

        if total_lines == 0:
            self.root.after(0, lambda: self._on_generation_error(
                "No dialogue lines to generate.", ""))
            return

        self._log_from_thread(f"Starting generation: {total_lines} dialogue lines", "header")
        self._log_from_thread(f"Project: {project_name}")
        self._log_from_thread(f"Output: {output_folder}")
        self._log_from_thread("-" * 50)

        config_manager = settings.get("config_manager")
        creds_path = config_manager.get_ui("google_credentials_path") if config_manager else ""
        audio_gen = AudioGenerator(credentials_path=creds_path or None)
        silence_trim_mode = settings.get("silence_trim_mode", "beginning_end")
        output_format = settings.get("output_format", "mp3")
        clip_ext = ".ogg" if output_format == "ogg" else ".mp3"
        clip_paths = {}  # line_number -> output path
        ref_entries = []  # (filename, speaker_id, spoken_text, is_inner_thought)
        errors = []

        # --- Phase 1: Generate individual clips ---
        self._log_from_thread("Phase 1: Generating individual voice clips...", "header")

        for i, line in enumerate(dialogue_lines):
            if self._gen_cancel_requested:
                self._log_from_thread("Generation cancelled by user.", "warning")
                self.root.after(0, self._on_generation_cancelled)
                return

            speaker_id = line.speaker_id
            sp = speaker_settings.get(speaker_id)
            if not sp:
                errors.append(f"Line {line.line_number}: No settings for speaker '{speaker_id}'")
                continue

            # Build filename
            clip_filename = FileManager.build_clip_filename(
                project_name, line.line_number, speaker_id, line.spoken_text,
                extension=clip_ext,
            )
            clean_path = clips_clean_folder / clip_filename
            effect_path = clips_effect_folder / clip_filename

            # Calculate speaking_rate with yell impact applied if applicable
            speaking_rate = sp['speaking_rate']
            yell_impact = sp['yell_impact']

            if yell_impact != 0 and is_yell_line(line.spoken_text):
                # yell_impact is stored as a negative int (e.g. -30)
                # Formula: clamp(speaking_rate * (1 + yell_impact/100), 0.25, 2.0)
                yell_rate = max(0.25, min(2.0, speaking_rate * (1.0 + yell_impact / 100.0)))
                self._log_from_thread(
                    f"  Line {line.line_number}: Yell impact applied "
                    f"(rate {speaking_rate:.2f}\u00d7 \u2192 {yell_rate:.2f}\u00d7)", "info")
                speaking_rate = yell_rate

            # Generate TTS directly to clips_clean (this IS the clean clip)
            success, tts_error = audio_gen.generate_audio(
                line.spoken_text, str(clean_path),
                sp['voice_name'],
                speaking_rate=speaking_rate,
                pitch_semitones=sp['pitch_semitones'],
                config_manager=config_manager,
                output_format=output_format,
            )
            if not success:
                errors.append(f"Line {line.line_number} TTS failed: {tts_error}")
                self._log_from_thread(
                    f"  Line {line.line_number}: TTS error - {tts_error}", "error")
                continue

            # Apply audio effects: clean -> effects version
            success, error_msg = audio_gen.apply_audio_effects(
                str(clean_path), str(effect_path),
                sp['effects'], sp['volume'],
                is_inner_thought=line.is_inner_thought,
                config_manager=config_manager,
                silence_trim_mode=silence_trim_mode,
                output_format=output_format,
            )

            if not success:
                errors.append(f"Line {line.line_number} effects failed: {error_msg}")
                self._log_from_thread(
                    f"  Line {line.line_number}: Effects error - {error_msg}", "error")
                continue

            # Peak-normalize the effect clip in-place (Tenacity-style: bring peak to 0dBFS)
            success, error_msg = audio_gen.apply_peak_normalize(
                str(effect_path), str(effect_path)
            )
            if not success:
                errors.append(f"Line {line.line_number} peak normalize failed: {error_msg}")
                self._log_from_thread(
                    f"  Line {line.line_number}: Peak normalize error - {error_msg}", "error")
                continue

            # Merger uses the effects clip
            clip_paths[line.line_number] = str(effect_path)
            ref_entries.append((clip_filename, speaker_id, line.spoken_text, line.is_inner_thought))

            # Progress update
            pct = ((i + 1) / total_lines) * 70  # Clips = 0-70%
            self._progress_from_thread(pct,
                                       f"Generating clip {i+1}/{total_lines}: "
                                       f"{speaker_id} (line {line.line_number})")

            if (i + 1) % 5 == 0 or (i + 1) == total_lines:
                self._log_from_thread(
                    f"  Generated {i+1}/{total_lines} clips", "info")

        if self._gen_cancel_requested:
            self._log_from_thread("Generation cancelled by user.", "warning")
            self.root.after(0, self._on_generation_cancelled)
            return

        clips_ok = len(clip_paths)
        self._log_from_thread(
            f"Phase 1 complete: {clips_ok}/{total_lines} clips generated "
            f"(clean → clips_clean/, effects → clips_effect/)", "success")

        if clips_ok == 0:
            self.root.after(0, lambda: self._on_generation_error(
                "No clips were generated successfully.", "\n".join(errors)))
            return

        # --- Phase 2: Process SFX files ---
        sfx_clip_paths = {}  # filename -> processed path in output folder
        sfx_included = settings["sfx_included"]
        sfx_source_paths = settings["sfx_paths"]
        sfx_effects = settings["sfx_effects"]

        has_active_sfx_effects = any(
            (v != 0.0 if isinstance(v, float) else v != "off")
            for v in sfx_effects.values()
        )

        # All found SFX files are always included in the output.
        # The sfx_included checkbox only controls whether effects are applied — unchecked
        # means "use this file as-is", not "omit this file from the merged audio".
        sfx_found = [fn for fn in sfx_source_paths]

        if sfx_found:
            sfx_folder = output_folder / "sfx"
            sfx_folder.mkdir(exist_ok=True)

            self._log_from_thread(f"\nPhase 2: Processing {len(sfx_found)} SFX files...",
                                  "header")
            for sfx_fn in sfx_found:
                if self._gen_cancel_requested:
                    self.root.after(0, self._on_generation_cancelled)
                    return

                source = sfx_source_paths[sfx_fn]
                # Always output as .mp3 — source may be .wav or any other format.
                # FFMPEG is doing a full decode→process→encode pass anyway, so the source
                # format doesn't affect quality. .mp3 keeps processed SFX compact and
                # consistent with the voice clips.
                base_name = FileManager.sanitize_filename(Path(sfx_fn).stem)
                dest = sfx_folder / f"sfx_{base_name}{clip_ext}"

                apply_effects = sfx_included.get(sfx_fn, True) and has_active_sfx_effects
                if apply_effects:
                    success, err = audio_gen.apply_audio_effects(
                        source, str(dest), sfx_effects, 100, False, is_sfx=True
                    )
                    if success:
                        sfx_clip_paths[sfx_fn] = str(dest)
                        self._log_from_thread(f"  Processed SFX (effects): {sfx_fn}", "info")
                    else:
                        self._log_from_thread(f"  SFX error ({sfx_fn}): {err}", "error")
                        # Fall back to original on error
                        sfx_clip_paths[sfx_fn] = source
                else:
                    # No effects (or effects disabled for this file) — use original path directly
                    sfx_clip_paths[sfx_fn] = source
                    self._log_from_thread(f"  SFX (no effects): {sfx_fn}", "info")
        else:
            self._log_from_thread("\nPhase 2: No SFX to process.", "info")

        self._progress_from_thread(75, "Building merged audio timeline...")

        # --- Phase 3: Merge clips ---
        self._log_from_thread("\nPhase 3: Building merged audio...", "header")

        merger = AudioMerger(self.config_manager)
        timeline = merger.build_timeline(result.lines, clip_paths, sfx_paths=sfx_clip_paths)

        pure_name = FileManager.build_merged_filename(project_name, "pure", extension=clip_ext)
        loudnorm_name = FileManager.build_merged_filename(project_name, "loudnorm", extension=clip_ext)
        pure_path = output_folder / pure_name
        loudnorm_path = output_folder / loudnorm_name

        self._progress_from_thread(80, "Merging clips (this may take a moment)...")

        success, merge_error = merger.merge_clips(
            timeline, str(pure_path), str(loudnorm_path),
            sfx_paths=sfx_clip_paths,
            output_format=output_format,
        )

        if success:
            self._log_from_thread(f"  Merged pure: {pure_name}", "success")
            self._log_from_thread(f"  Merged loudnorm: {loudnorm_name}", "success")
        else:
            self._log_from_thread(f"  Merge failed: {merge_error}", "error")
            errors.append(f"Merge failed: {merge_error}")

        self._progress_from_thread(90, "Generating reference sheet...")

        # --- Phase 4: Reference sheet ---
        self._log_from_thread("\nPhase 4: Generating reference sheet...", "header")

        ref_filename = f"{FileManager.sanitize_filename(project_name)}_reference.txt"
        ref_path = output_folder / ref_filename
        sound_count = len({e.filename for e in result.sound_effects})
        FileManager.generate_reference_sheet(
            ref_entries,
            str(ref_path),
            project_name=project_name,
            output_format=output_format,
            speaker_settings=speaker_settings,
            config_manager=config_manager,
            sfx_effects=settings.get("sfx_effects", {}),
            sound_count=sound_count,
        )
        self._log_from_thread(f"  Reference sheet: {ref_filename}", "success")

        # --- Done ---
        self._progress_from_thread(100, "Generation complete!")
        self._log_from_thread("\n" + "=" * 50)

        if errors:
            self._log_from_thread(f"\nCompleted with {len(errors)} error(s):", "warning")
            for err in errors:
                self._log_from_thread(f"  - {err}", "warning")
        else:
            self._log_from_thread("\nAll files generated successfully!", "success")

        self._log_from_thread(
            f"\nOutput folder: {output_folder}\n"
            f"Clean clips: clips_clean/ ({clips_ok} files)\n"
            f"Effects clips: clips_effect/ ({clips_ok} files)\n"
            f"Merged files: {'2' if success else '0 (failed)'}\n"
            f"Reference sheet: {ref_filename}",
            "info"
        )

        # Save project name to config
        self.root.after(0, lambda: self._on_generation_done(
            str(output_folder), clips_ok, bool(success), len(errors)))

    # ── Thread-safe UI callbacks ─────────────────────────────

    def _log_from_thread(self, message, tag=None):
        """Thread-safe: append to generation log."""
        self.root.after(0, lambda: self.gen_log(message, tag))

    def _progress_from_thread(self, value, label=None):
        """Thread-safe: update progress bar."""
        self.root.after(0, lambda: self.gen_progress(value, label))

    def _on_generation_done(self, output_folder, clips_count, merge_ok, error_count):
        """Called on main thread when generation completes successfully."""
        self._gen_running = False
        self._btn_generate.config(state="normal")
        self._btn_cancel.config(state="disabled")
        self._btn_open_output.config(state="normal")

        # Remember the actual resolved output folder so Open Output Folder opens it directly
        self._last_resolved_output_folder = output_folder

        # Persist settings
        self.config_manager.set_ui("last_project_name",
                                   self._gen_project_name_var.get().strip())
        self.config_manager.set_ui("last_output_folder",
                                   self._gen_output_folder_var.get().strip())

        if hasattr(self, 'status_label'):
            self.status_label.config(
                text=f"Generation complete! {clips_count} clips"
                     f"{', merged' if merge_ok else ''}"
                     f"{f', {error_count} errors' if error_count else ''}")

    def _on_generation_error(self, message, tb):
        """Called on main thread when generation fails fatally."""
        self._gen_running = False
        self._btn_generate.config(state="normal")
        self._btn_cancel.config(state="disabled")

        self.gen_log(f"\nFATAL ERROR: {message}", "error")
        if tb:
            self.gen_log(tb, "error")
        self.gen_progress(0, "Generation failed.")

        if hasattr(self, 'status_label'):
            self.status_label.config(text="Generation failed.")

    def _on_generation_cancelled(self):
        """Called on main thread when generation is cancelled."""
        self._gen_running = False
        self._btn_generate.config(state="normal")
        self._btn_cancel.config(state="disabled")
        self.gen_progress(0, "Cancelled.")

        if hasattr(self, 'status_label'):
            self.status_label.config(text="Generation cancelled.")
