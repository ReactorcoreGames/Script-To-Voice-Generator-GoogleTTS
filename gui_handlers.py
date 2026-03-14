"""
Event handlers for Script to Voice Generator GUI.
Tab 1 handlers for script loading, parsing, and navigation.
Tab 2 handlers for voice testing, apply-to-all, SFX scanning, profiles.
Tab 3 handlers for generation controls, output folder, open output.
"""

import os
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import ttkbootstrap as ttk

import re

from config import AUDIO_EFFECTS, APP_THEME, ICON_FILENAME, INVALID_FILENAME_CHARS
from script_parser import parse_script


class GUIHandlers:
    """Mixin class containing event handlers"""

    # ── Tab 1 handlers ──────────────────────────────────────────

    def on_load_script(self):
        """Handle 'Open Script File' button click."""
        initial_dir = self.config_manager.get_ui("last_script_folder")
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()

        filepath = filedialog.askopenfilename(
            title="Select Script File",
            initialdir=initial_dir,
            filetypes=[
                ("Script files", "*.txt *.md"),
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*"),
            ]
        )

        if not filepath:
            return

        # Remember the folder
        self.config_manager.set_ui("last_script_folder", str(Path(filepath).parent))

        self._current_script_path = filepath
        self._run_parse(filepath)

    def on_reload_script(self):
        """Handle 'Reload Script' button click."""
        if hasattr(self, '_current_script_path') and self._current_script_path:
            self._run_parse(self._current_script_path)
        else:
            messagebox.showinfo("No Script", "No script file has been loaded yet.")

    def on_open_script_folder(self):
        """Open the folder containing the currently loaded script file."""
        if not hasattr(self, '_current_script_path') or not self._current_script_path:
            return
        folder = str(Path(self._current_script_path).parent)
        try:
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

    def _run_parse(self, filepath):
        """Run the parser on a script file and update the UI."""
        self.clear_log()
        self.reset_stats()

        # Update file label
        filename = Path(filepath).name
        self.loaded_file_label.config(text=f"File: {filepath}",
                                     foreground="#C8D8F0")

        # Prefill Tab 3 project name from filename (first 20 chars, sanitized)
        stem = Path(filepath).stem
        sanitized = re.sub(f"[{''.join(re.escape(c) for c in INVALID_FILENAME_CHARS)}]",
                           "_", stem)
        sanitized = re.sub(r"[\s_]+", "_", sanitized).strip("_")
        prefill = sanitized[:20]
        if prefill:
            self._gen_project_name_var.set(prefill)

        self.log_message(f"Parsing: {filename}", "header")
        self.log_message("-" * 60)

        # Parse the script
        result = parse_script(filepath)
        self._last_parse_result = result

        # Log errors
        if result.errors:
            self.log_message(f"\n{len(result.errors)} error(s) found:", "error")
            for err in result.errors:
                self.log_message(f"  Line {err.line_number}: {err.message}", "error")
                if err.line_content:
                    content = err.line_content[:80]
                    if len(err.line_content) > 80:
                        content += "..."
                    self.log_message(f"    > {content}", "warning")
            self.log_message("")

        # Log speakers found
        if result.speakers:
            self.log_message(f"Found {len(result.speakers)} unique speaker(s):", "info")
            for i, speaker in enumerate(result.speakers, 1):
                existing = self.char_profiles.get_profile(speaker)
                status = " (known)" if existing else " (new)"
                self.log_message(f"  {i}. {speaker}{status}", "info")
            self.log_message("")

        # Log sound effects
        if result.sound_effects:
            self.log_message(f"Found {len(result.sound_effects)} sound effect file(s) referenced:", "info")
            for sfx in result.sound_effects:
                lines_str = ", ".join(str(ln) for ln in sfx.line_numbers)
                self.log_message(f"  - {sfx.filename} (lines: {lines_str})", "info")
            self.log_message("")

        # Summary
        if result.errors:
            self.log_message(
                f"Script has {len(result.errors)} error(s). "
                f"Fix them and reload to continue.",
                "error"
            )
        else:
            self.log_message(
                f"Script parsed successfully! "
                f"{result.total_dialogue_lines} dialogue lines, "
                f"{len(result.speakers)} speakers, "
                f"{len(result.sound_effects)} sound effects.",
                "success"
            )

        # Update stats panel
        self.update_stats(result)

        # Enable/disable buttons
        self.btn_reload_script.config(state="normal")

        if not result.errors and result.total_dialogue_lines > 0:
            self.btn_continue_to_tab2.config(state="normal")
            # Auto-register speakers in character profiles
            self.char_profiles.ensure_speakers(result.speakers)
            # Populate Tab 2 with speaker panels
            self.populate_tab2_speakers(result.speakers, result)
        else:
            self.btn_continue_to_tab2.config(state="disabled")

        # Enable the open-script-folder button now that a script is loaded
        self.btn_open_script_folder.config(state="normal")

        # Re-scan SFX folder so found/missing statuses stay current after reload
        sfx_folder = self._sfx_folder_var.get() if hasattr(self, '_sfx_folder_var') else ""
        if sfx_folder and os.path.isdir(sfx_folder):
            self._scan_sfx_folder(sfx_folder)
        elif result.sound_effects and not sfx_folder:
            self.log_message(
                f"Warning: script references {len(result.sound_effects)} sound effect file(s) "
                f"but no SFX folder is set. Go to Tab 2 to select one.",
                "warning"
            )

        # Mark Tab 3 summary as outdated
        if hasattr(self, '_summary_status_label'):
            self._summary_status_label.config(text="Summary outdated — click Refresh",
                                              foreground="#FFD43B")

    def on_continue_to_tab2(self):
        """Navigate to Tab 2."""
        self.notebook.select(1)

    def on_help(self):
        """Open the README in the system default text editor."""
        if getattr(sys, 'frozen', False):
            app_path = Path(sys.executable).parent
        else:
            app_path = Path(__file__).parent
        readme_path = app_path / "README.md"
        if not readme_path.exists():
            messagebox.showinfo("Help",
                              "README.md not found.\n\n"
                              "Load a script file (.txt or .md) with the correct format:\n"
                              "  SpeakerID: Dialogue text here.\n\n"
                              "Each non-blank line needs a speaker ID followed by a colon.\n"
                              "Use // or # for comments, (1.5s) for pauses,\n"
                              "and {play file.mp3} for sound effects.")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(str(readme_path))
            elif sys.platform == 'darwin':
                subprocess.run(["open", str(readme_path)])
            else:
                subprocess.run(["xdg-open", str(readme_path)])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open README: {e}")

    # ── Tab 2 handlers ──────────────────────────────────────────

    def on_apply_to_all(self):
        """Apply the 'Apply to All' effect settings to every speaker panel."""
        if not self._speaker_vars:
            messagebox.showinfo("No Speakers", "No speakers loaded. Load a script first.")
            return

        for effect_name, apply_var in self._apply_all_vars.items():
            value = apply_var.get()
            for speaker_id, vars_dict in self._speaker_vars.items():
                if effect_name in vars_dict:
                    vars_dict[effect_name].set(value)

        if hasattr(self, 'status_label'):
            self.status_label.config(text="Audio effects applied to all speakers.")

    def on_test_voice(self, speaker_id):
        """Generate a test voice clip for a speaker."""
        if speaker_id not in self._speaker_vars:
            return

        vars_dict = self._speaker_vars[speaker_id]

        # Get voice short name
        voice_val = vars_dict["voice"].get()
        if " | " in voice_val:
            voice_name = voice_val.split(" | ")[0]
        elif voice_val:
            voice_name = voice_val
        else:
            messagebox.showwarning("No Voice", f"Select a voice for {speaker_id} first.")
            return

        # Get pitch and speed
        pitch_semitones = vars_dict["pitch_semitones"].get()
        speaking_rate = vars_dict["speaking_rate"].get()

        # Get effect settings
        effect_settings = {}
        for effect_name in AUDIO_EFFECTS:
            effect_settings[effect_name] = vars_dict[effect_name].get()

        volume = vars_dict["volume_percent"].get()
        effect_settings["fmsu"] = vars_dict["fmsu"].get()
        effect_settings["reverse"] = vars_dict["reverse"].get()
        # Note: yell_impact_percent is stored in profile but not applied to the fixed test text

        # Generate in background thread
        test_text = self._test_text_var.get().strip() or "The quick brown fox jumps over the lazy dog."

        if hasattr(self, 'status_label'):
            self.status_label.config(text=f"Generating test voice for {speaker_id}...")

        def generate():
            try:
                from file_manager import FileManager
                output_format = self.config_manager.get_output_format()
                clip_ext = ".ogg" if output_format == "ogg" else ".mp3"
                test_dir = FileManager.get_test_output_dir()
                raw_path = test_dir / f"_test_{speaker_id}_raw{clip_ext}"
                final_path = test_dir / f"test_{speaker_id}{clip_ext}"

                # Check if the output file is locked (e.g. still playing in media player)
                if final_path.exists():
                    try:
                        final_path.rename(final_path)
                    except PermissionError:
                        self.root.after(0, lambda: self._on_test_voice_done(
                            speaker_id, None,
                            "The previous test clip is still open in your media player.\n\n"
                            "Close or stop it, then click Test Voice again."))
                        return

                # Generate TTS
                success, error = self.audio_gen.generate_audio(
                    test_text, str(raw_path), voice_name,
                    speaking_rate=speaking_rate,
                    pitch_semitones=pitch_semitones,
                    config_manager=self.config_manager,
                    output_format=output_format,
                )
                if not success:
                    self.root.after(0, lambda: self._on_test_voice_done(
                        speaker_id, None, error))
                    return

                # Apply effects
                silence_mode = self.config_manager.get_silence_trim("mode") or "beginning_end"
                success, error = self.audio_gen.apply_audio_effects(
                    str(raw_path), str(final_path),
                    effect_settings, volume,
                    silence_trim_mode=silence_mode,
                )

                # Clean up raw file
                try:
                    raw_path.unlink(missing_ok=True)
                except Exception:
                    pass

                if success:
                    # Peak-normalize to match what Generate All produces
                    success, error = self.audio_gen.apply_peak_normalize(
                        str(final_path), str(final_path)
                    )

                if success:
                    self.root.after(0, lambda p=str(final_path): self._on_test_voice_done(
                        speaker_id, p, None))
                else:
                    self.root.after(0, lambda: self._on_test_voice_done(
                        speaker_id, None, error))

            except Exception as e:
                self.root.after(0, lambda: self._on_test_voice_done(
                    speaker_id, None, str(e)))

        threading.Thread(target=generate, daemon=True).start()

    def on_test_voice_inner_thoughts(self, speaker_id):
        """Generate a test voice clip with the speaker's effects plus the inner thoughts filter."""
        if speaker_id not in self._speaker_vars:
            return

        vars_dict = self._speaker_vars[speaker_id]

        voice_val = vars_dict["voice"].get()
        if " | " in voice_val:
            voice_name = voice_val.split(" | ")[0]
        elif voice_val:
            voice_name = voice_val
        else:
            messagebox.showwarning("No Voice", f"Select a voice for {speaker_id} first.")
            return

        pitch_semitones = vars_dict["pitch_semitones"].get()
        speaking_rate = vars_dict["speaking_rate"].get()

        effect_settings = {}
        for effect_name in AUDIO_EFFECTS:
            effect_settings[effect_name] = vars_dict[effect_name].get()

        volume = vars_dict["volume_percent"].get()
        effect_settings["fmsu"] = vars_dict["fmsu"].get()
        effect_settings["reverse"] = vars_dict["reverse"].get()

        test_text = self._test_text_var.get().strip() or "The quick brown fox jumps over the lazy dog."

        if hasattr(self, 'status_label'):
            self.status_label.config(
                text=f"Generating inner thoughts test for {speaker_id}...")

        def generate():
            try:
                from file_manager import FileManager
                output_format = self.config_manager.get_output_format()
                clip_ext = ".ogg" if output_format == "ogg" else ".mp3"
                test_dir = FileManager.get_test_output_dir()
                raw_path = test_dir / f"_test_{speaker_id}_it_raw{clip_ext}"
                final_path = test_dir / f"test_{speaker_id}_it{clip_ext}"

                if final_path.exists():
                    try:
                        final_path.rename(final_path)
                    except PermissionError:
                        self.root.after(0, lambda: self._on_test_voice_done(
                            speaker_id, None,
                            "The previous inner thoughts test clip is still open in your media player.\n\n"
                            "Close or stop it, then click Test + Inner Thoughts again."))
                        return

                success, error = self.audio_gen.generate_audio(
                    test_text, str(raw_path), voice_name,
                    speaking_rate=speaking_rate,
                    pitch_semitones=pitch_semitones,
                    config_manager=self.config_manager,
                    output_format=output_format,
                )
                if not success:
                    self.root.after(0, lambda: self._on_test_voice_done(
                        speaker_id, None, error))
                    return

                silence_mode = self.config_manager.get_silence_trim("mode") or "beginning_end"
                success, error = self.audio_gen.apply_audio_effects(
                    str(raw_path), str(final_path),
                    effect_settings, volume,
                    is_inner_thought=True,
                    config_manager=self.config_manager,
                    silence_trim_mode=silence_mode,
                )

                try:
                    raw_path.unlink(missing_ok=True)
                except Exception:
                    pass

                if success:
                    # Peak-normalize to match what Generate All produces
                    success, error = self.audio_gen.apply_peak_normalize(
                        str(final_path), str(final_path)
                    )

                if success:
                    self.root.after(0, lambda p=str(final_path): self._on_test_voice_done(
                        speaker_id, p, None))
                else:
                    self.root.after(0, lambda: self._on_test_voice_done(
                        speaker_id, None, error))

            except Exception as e:
                self.root.after(0, lambda: self._on_test_voice_done(
                    speaker_id, None, str(e)))

        threading.Thread(target=generate, daemon=True).start()

    def _on_test_voice_done(self, speaker_id, filepath, error):
        """Callback when test voice generation completes."""
        if error:
            messagebox.showerror("Test Voice Error",
                               f"Failed to generate test for {speaker_id}:\n\n{error}")
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Test voice failed for {speaker_id}.")
        else:
            if hasattr(self, 'status_label'):
                self.status_label.config(text=f"Test voice saved: {filepath}")
            # Auto-open in default media player
            try:
                if sys.platform == 'win32':
                    os.startfile(filepath)
                elif sys.platform == 'darwin':
                    subprocess.run(["open", filepath])
                else:
                    subprocess.run(["xdg-open", filepath])
            except Exception:
                pass  # Don't fail if media player can't open

    def on_pick_sfx_folder(self):
        """Handle SFX folder selection."""
        initial_dir = self.config_manager.get_ui("last_sfx_folder")
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()

        folder = filedialog.askdirectory(
            title="Select Sound Effects Folder",
            initialdir=initial_dir,
        )

        if not folder:
            return

        self.config_manager.set_ui("last_sfx_folder", folder)
        self._sfx_folder_var.set(folder)
        self._scan_sfx_folder(folder)

    def on_open_profiles(self):
        """Open character_profiles.json in the system editor."""
        self.char_profiles.open_in_editor()

    def on_continue_to_tab3(self):
        """Navigate to Tab 3 and refresh the summary."""
        self.notebook.select(2)
        self._refresh_summary()

    # ── Tab 3 handlers ──────────────────────────────────────────

    def _on_pick_output_folder(self):
        """Handle output folder selection for generation."""
        initial_dir = self.config_manager.get_ui("last_output_folder")
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = os.getcwd()

        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=initial_dir,
        )

        if folder:
            self._gen_output_folder_var.set(folder)
            self.config_manager.set_ui("last_output_folder", folder)

    def _on_generate_clicked(self):
        """Handle 'Generate All' button click."""
        from config import MAX_PROJECT_NAME_LENGTH, INVALID_FILENAME_CHARS

        # Validate prerequisites
        result = getattr(self, '_last_parse_result', None)
        if not result or not result.speakers:
            messagebox.showwarning("No Script",
                                   "No script loaded. Go to Tab 1 to load a script.")
            return

        project_name = self._gen_project_name_var.get().strip()
        if not project_name:
            messagebox.showwarning("Project Name",
                                   "Enter a project name before generating.")
            return

        if len(project_name) > MAX_PROJECT_NAME_LENGTH:
            messagebox.showwarning("Project Name",
                                   f"Project name exceeds {MAX_PROJECT_NAME_LENGTH} characters.")
            return

        bad_chars = [ch for ch in project_name if ch in INVALID_FILENAME_CHARS]
        if bad_chars:
            messagebox.showwarning("Project Name",
                                   f"Project name contains invalid characters: "
                                   f"{', '.join(repr(c) for c in bad_chars)}")
            return

        output_folder = self._gen_output_folder_var.get().strip()
        if not output_folder:
            messagebox.showwarning("Output Folder",
                                   "Select an output folder before generating.")
            return

        # Check that all speakers have voices assigned
        for speaker_id in result.speakers:
            vars_dict = self._speaker_vars.get(speaker_id, {})
            voice_val = vars_dict.get("voice")
            if not voice_val or not voice_val.get():
                messagebox.showwarning("Missing Voice",
                                       f"Speaker '{speaker_id}' has no voice assigned.\n"
                                       f"Go to Tab 2 to select a voice.")
                return

        # Confirm with user
        total = result.total_dialogue_lines
        use_subfolder = self._gen_use_project_subfolder_var.get()
        from pathlib import Path as _Path
        resolved_output = str(_Path(output_folder) / project_name) if use_subfolder else output_folder
        confirm = messagebox.askyesno(
            "Start Generation",
            f"Generate {total} voice clips?\n\n"
            f"Project: {project_name}\n"
            f"Output: {resolved_output}\n\n"
            f"This may take several minutes."
        )
        if not confirm:
            return

        # Start generation (defined in gui_generation.py GenerationMixin)
        self.run_generation()

    def _on_cancel_clicked(self):
        """Handle 'Cancel' button click during generation."""
        self._gen_cancel_requested = True
        self._btn_cancel.config(state="disabled")
        self.gen_log("Cancellation requested... finishing current clip.", "warning")

    def _on_open_output_folder(self):
        """Open the output folder in the system file manager."""
        # Prefer the resolved folder (may include project subfolder) set after generation
        folder = getattr(self, '_last_resolved_output_folder', None) or \
                 self._gen_output_folder_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showinfo("No Folder",
                               "Output folder does not exist yet.")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':
                subprocess.run(["open", folder])
            else:
                subprocess.run(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {e}")

    # ── Voice loading ───────────────────────────────────────────

    def _load_voices_async(self):
        """Start loading Google TTS voices in a background thread."""
        def load():
            try:
                creds_path = self.config_manager.get_ui("google_credentials_path")
                voices = self.audio_gen.load_voices(credentials_path=creds_path or None)
                self.root.after(0, self._on_voices_loaded, voices, None)
            except Exception as e:
                self.root.after(0, self._on_voices_loaded, [], str(e))

        threading.Thread(target=load, daemon=True).start()

    def _on_voices_loaded(self, voices, error=None):
        """Callback when voices finish loading."""
        self._available_voices = voices
        self._voices_loaded = True

        show_retry = False
        if hasattr(self, 'status_label'):
            if error:
                show_retry = True
                if "SERVICE_DISABLED" in error or "has not been used" in error:
                    self.status_label.config(
                        text="Error: Cloud Text-to-Speech API is not enabled on your Google Cloud project. "
                             "Go to APIs & Services > Library and enable it.")
                elif "PERMISSION_DENIED" in error or "403" in error:
                    self.status_label.config(
                        text="Error: Permission denied. Check that your service account has Text-to-Speech access.")
                elif "not found" in error.lower() or "No such file" in error:
                    self.status_label.config(
                        text="Error: Credentials file not found. Check the path in Tab 4.")
                else:
                    self.status_label.config(
                        text=f"Error loading voices: {error[:120]}")
            elif voices:
                self.status_label.config(text=f"Loaded {len(voices)} voices.")
            else:
                show_retry = True
                self.status_label.config(
                    text="No voices loaded. Check credentials in Tab 4.")

        if hasattr(self, 'retry_voices_btn'):
            if show_retry:
                self.retry_voices_btn.config(state="normal")
                self.retry_voices_btn.pack(side="left", padx=(4, 0))
            else:
                self.retry_voices_btn.pack_forget()

        # If speakers are already shown, populate their comboboxes
        if self._speaker_vars:
            self._set_voices_on_comboboxes()

    def _on_retry_voices(self):
        """Retry loading voices after a failed attempt."""
        if hasattr(self, 'retry_voices_btn'):
            self.retry_voices_btn.config(state="disabled")
            self.retry_voices_btn.pack_forget()
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Retrying voice load...")
        self._load_voices_async()

    # ── Welcome popup ────────────────────────────────────────────────────────

    def _show_welcome_if_enabled(self):
        """Show credentials popup (if not set) then welcome popup (if enabled)."""
        creds = self.config_manager.get_ui("google_credentials_path")
        if not creds or not os.path.isfile(creds):
            self._show_credentials_popup()
        elif self.config_manager.get_ui("show_welcome_popup"):
            self._show_welcome_popup()

    def _show_credentials_popup(self):
        """
        First-launch popup: welcome orientation + Google Cloud credentials setup.
        Shows when credentials path is not set or file is missing.
        """
        import webbrowser
        colors = APP_THEME["colors"]
        muted = "#8AAAC8"

        popup = tk.Toplevel(self.root)
        popup.title("Welcome — Script to Voice Generator")
        popup.resizable(False, False)
        popup.configure(bg=colors["bg"])
        popup.transient(self.root)
        popup.grab_set()

        try:
            if getattr(sys, 'frozen', False):
                icon_path = Path(sys.executable).parent / ICON_FILENAME
            else:
                icon_path = Path(__file__).parent / ICON_FILENAME
            if icon_path.exists():
                popup.iconbitmap(str(icon_path))
        except Exception:
            pass

        content = ttk.Frame(popup, padding=(28, 24, 28, 20))
        content.pack(fill="both", expand=True)

        # ── Title ────────────────────────────────────────────────
        ttk.Label(
            content,
            text="Welcome to Script to Voice Generator",
            font=("Consolas", 14, "bold"),
            foreground=colors["accent"],
        ).pack(anchor="w", pady=(0, 4))

        ttk.Label(
            content,
            text="by Reactorcore",
            font=("Consolas", 9),
            foreground=muted,
        ).pack(anchor="w", pady=(0, 14))

        # ── What the app does ─────────────────────────────────────
        ttk.Label(
            content,
            text="This app turns a formatted script file into a fully voiced audio file.\n"
                 "Each character gets their own voice, effects, and pacing — then everything\n"
                 "is stitched together into a single MP3 you can use anywhere.",
            font=("Consolas", 10),
            foreground=colors["fg"],
            justify="left",
        ).pack(anchor="w", pady=(0, 14))

        # ── Quick start steps ─────────────────────────────────────
        ttk.Label(
            content,
            text="How it works:",
            font=("Consolas", 10, "bold"),
            foreground=colors["fg"],
        ).pack(anchor="w", pady=(0, 4))

        steps = [
            ("1.", "Write or load a script file  (.txt or .md)"),
            ("2.", "Assign a voice to each character  (Tab 2)"),
            ("3.", "Pick an output folder and click Generate  (Tab 3)"),
        ]
        for num, text in steps:
            row = ttk.Frame(content)
            row.pack(anchor="w", fill="x")
            ttk.Label(row, text=num, font=("Consolas", 10, "bold"),
                      foreground=colors["accent"], width=3).pack(side="left")
            ttk.Label(row, text=text, font=("Consolas", 10),
                      foreground=colors["fg"]).pack(side="left")

        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=(16, 14))

        # ── Credentials section ───────────────────────────────────
        ttk.Label(
            content,
            text="One-time setup: Google Cloud API key",
            font=("Consolas", 11, "bold"),
            foreground=colors["fg"],
        ).pack(anchor="w", pady=(0, 6))

        ttk.Label(
            content,
            text="The voices are powered by Google Cloud Text-to-Speech. You need a Google\n"
                 "Cloud account and a service account key file (a .json file). Google's console\n"
                 "has some confusing dead ends right now — read the local guide first.",
            font=("Consolas", 10),
            foreground=colors["fg"],
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        def open_gcloud_guide():
            webbrowser.open("https://console.cloud.google.com")

        def open_local_guide():
            import os
            if getattr(sys, 'frozen', False):
                base = Path(sys.executable).parent
            else:
                base = Path(__file__).parent
            guide = base / "!docs" / "guides" / "Google_Cloud_Setup_Guide.md"
            if guide.exists():
                os.startfile(str(guide))

        ttk.Button(
            content,
            text="Open Google Cloud Console  ↗",
            command=open_gcloud_guide,
            bootstyle="info-outline",
            width=36,
        ).pack(anchor="w", pady=(0, 6))

        ttk.Button(
            content,
            text="Open Local Setup Guide",
            command=open_local_guide,
            bootstyle="secondary-outline",
            width=36,
        ).pack(anchor="w", pady=(0, 12))

        ttk.Label(
            content,
            text="Once you have the .json key file, point this app to it:",
            font=("Consolas", 10),
            foreground=muted,
        ).pack(anchor="w", pady=(0, 6))

        path_var = tk.StringVar(value=self.config_manager.get_ui("google_credentials_path"))

        path_row = ttk.Frame(content)
        path_row.pack(fill="x", pady=(0, 4))

        ttk.Label(path_row, text="Key file (.json):",
                  font=("Consolas", 10)).pack(side="left", padx=(0, 8))

        path_entry = ttk.Entry(path_row, textvariable=path_var,
                               width=36, font=("Consolas", 9))
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def browse():
            fp = filedialog.askopenfilename(
                title="Select Google Cloud Service Account JSON",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if fp:
                path_var.set(fp)

        ttk.Button(path_row, text="Browse...", command=browse,
                   bootstyle="info", width=10).pack(side="left")

        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=(14, 12))

        # ── Bottom buttons ────────────────────────────────────────
        btn_row = ttk.Frame(content)
        btn_row.pack(fill="x")

        def on_set():
            fp = path_var.get().strip()
            if fp and os.path.isfile(fp):
                self.config_manager.set_ui("google_credentials_path", fp)
                self.audio_gen._init_client(fp)
                # Sync the Tab 4 credentials entry if it's already built
                if hasattr(self, '_creds_path_var'):
                    self._creds_path_var.set(fp)
                popup.destroy()
                self._load_voices_async()
            else:
                messagebox.showwarning(
                    "Invalid Path",
                    "That file doesn't exist.\nCheck the path and try again.",
                    parent=popup,
                )

        def on_skip():
            popup.destroy()

        ttk.Button(btn_row, text="Set & Continue", command=on_set,
                   bootstyle="primary", width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Skip for now", command=on_skip,
                   bootstyle="secondary", width=14).pack(side="left")

        ttk.Label(btn_row, text="(you can set this later in Tab 4)",
                  font=("Consolas", 9), foreground=muted).pack(side="left", padx=(10, 0))

        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

    def _show_welcome_popup(self):
        """
        Display the welcome/orientation Toplevel dialog.
        Uses transient() without grab_set() to avoid Windows minimize/restore softlock.
        """
        colors = APP_THEME["colors"]

        popup = tk.Toplevel(self.root)
        popup.title("Welcome")
        popup.resizable(False, False)
        popup.configure(bg=colors["bg"])
        popup.transient(self.root)  # floats above main window; no modal grab

        try:
            if getattr(sys, 'frozen', False):
                app_path = Path(sys.executable).parent
            else:
                app_path = Path(__file__).parent
            icon_path = app_path / ICON_FILENAME
            if icon_path.exists():
                popup.iconbitmap(str(icon_path))
        except Exception:
            pass

        content = ttk.Frame(popup, padding=24)
        content.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            content,
            text="Welcome to Script to Voice Generator",
            font=("Consolas", 14, "bold"),
            foreground=colors["accent"],
        ).pack(anchor="w", pady=(0, 12))

        # Body
        body_lines = [
            "This app converts formatted script files (.txt / .md)",
            "into fully voiced audio using Google Cloud TTS (Chirp 3 HD).",
            "",
            "Quick start:",
            "  1.  Tab 1 — Load a script file",
            "  2.  Tab 2 — Assign a voice to each speaker",
            "  3.  Tab 3 — Set an output folder and generate",
            "",
            "Need to change your API key? Go to Tab 4 — Settings.",
            "",
            "Click  Help  (top-right) to open the full README guide.",
        ]
        for line in body_lines:
            ttk.Label(
                content,
                text=line,
                font=("Consolas", 10),
                foreground=colors["fg"],
                justify="left",
            ).pack(anchor="w")

        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=(16, 12))

        # "Don't show again" checkbox
        dont_show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            content,
            text="Don't show this again",
            variable=dont_show_var,
            bootstyle="secondary",
        ).pack(anchor="w", pady=(0, 12))

        # OK button
        def on_ok():
            if dont_show_var.get():
                self.config_manager.set_ui("show_welcome_popup", False)
            popup.destroy()

        ttk.Button(
            content,
            text="OK",
            command=on_ok,
            bootstyle="primary",
            width=12,
        ).pack(anchor="center", pady=(0, 4))

        # Center over main window after layout is calculated
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
