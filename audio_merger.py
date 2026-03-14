"""
Audio merger for Script to Voice Generator.
Takes individual generated clips + timeline events (pauses, play/stop commands)
and produces merged audio files with smart pause calculation.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _get_subprocess_startupinfo():
    """Get subprocess startup info to hide console windows on Windows."""
    if sys.platform == 'win32':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        return startupinfo
    return None


def _get_audio_duration_ms(filepath):
    """Get duration of an audio file in milliseconds using ffprobe."""
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(filepath)
        ], capture_output=True, text=True, startupinfo=_get_subprocess_startupinfo())
        return int(float(result.stdout.strip()) * 1000)
    except Exception:
        return 0


def _detect_end_punctuation(text):
    """
    Detect the ending punctuation type for pause calculation.
    Returns the punctuation key for config lookup.
    """
    text = text.rstrip()
    if not text:
        return "period"

    # Check for multi-character punctuation first
    if text.endswith('...'):
        return "ellipsis"
    if text.endswith('!!!') or text.endswith('?!?') or text.endswith('!?!'):
        return "triple_power"
    if text.endswith('!!') or text.endswith('?!') or text.endswith('!?'):
        return "double_power"

    last_char = text[-1]
    if last_char == '.':
        return "period"
    elif last_char == ',':
        return "comma"
    elif last_char == '!':
        return "exclamation"
    elif last_char == '?':
        return "question"
    elif last_char == '-' or text.endswith('--'):
        return "hyphen"
    else:
        return "period"


class AudioMerger:
    """
    Merges individual voice clips into continuous audio files
    with smart pauses and optional SFX mixing.
    """

    def __init__(self, config_manager):
        self.config = config_manager

    def calculate_pause_after(self, parsed_line, next_line=None, is_first=False, is_last=False):
        """
        Calculate the pause duration (in seconds) after a given dialogue line.

        Uses:
        - End-of-line punctuation to determine base pause
        - Contextual modifiers (speaker change, line length, inner thoughts)

        Args:
            parsed_line: The current ParsedLine
            next_line: The next ParsedLine (or None if last)
            is_first: Whether this is the first dialogue line
            is_last: Whether this is the last dialogue line

        Returns:
            float: pause duration in seconds
        """
        if parsed_line.line_type != "dialogue":
            return 0.0

        # Base pause from end punctuation
        punct_type = _detect_end_punctuation(parsed_line.spoken_text)
        base_pause = self.config.get_pause(punct_type)
        pause = base_pause

        # Contextual modifier: speaker change bonus
        if next_line and next_line.line_type == "dialogue":
            if next_line.speaker_id != parsed_line.speaker_id:
                pause += self.config.get_modifier("speaker_change_bonus")
            else:
                pause -= self.config.get_modifier("same_speaker_reduction_s")

        # Contextual modifier: line length adjustment
        text_len = len(parsed_line.spoken_text)
        short_threshold = self.config.get_modifier("short_line_threshold_chars")
        long_threshold = self.config.get_modifier("long_line_threshold_chars")

        if text_len <= short_threshold:
            pause -= self.config.get_modifier("short_line_reduction_s")
        elif text_len >= long_threshold:
            pause += self.config.get_modifier("long_line_addition_s")

        # Contextual modifier: inner thought padding
        if parsed_line.is_inner_thought:
            pause += self.config.get_modifier("inner_thought_padding_s")

        # Contextual modifier: last line padding (appended after last clip)
        if is_last:
            pause += self.config.get_modifier("last_line_padding_s")

        return max(0.0, round(pause, 2))

    def build_timeline(self, parsed_lines, clip_paths, sfx_paths=None):
        """
        Build a timeline of audio events from parsed lines and generated clips.

        Args:
            parsed_lines: List of ParsedLine objects (all types, in order)
            clip_paths: Dict mapping line_number -> path to generated audio clip
            sfx_paths: Dict mapping sfx filename -> resolved/processed file path

        Returns:
            list of timeline events
        """
        if sfx_paths is None:
            sfx_paths = {}

        timeline = []
        current_ms = 0

        dialogue_lines = [l for l in parsed_lines if l.line_type == "dialogue"]
        dialogue_count = len(dialogue_lines)

        # Determine the last "active" line (dialogue, pause, or play_command) so we can
        # correctly assign is_last only to the dialogue line that truly ends the script.
        # This prevents last_line_padding from being inserted before a trailing SFX or
        # explicit pause that follows the final dialogue line.
        active_types = {"dialogue", "pause", "play_command"}
        active_lines = [l for l in parsed_lines if l.line_type in active_types]
        last_active = active_lines[-1] if active_lines else None

        first_clip_added = False

        for line in parsed_lines:
            if line.line_type in ("blank", "comment", "heading"):
                continue

            if line.line_type == "dialogue":
                clip_path = clip_paths.get(line.line_number)
                if not clip_path or not Path(clip_path).exists():
                    continue

                # Inject first-line padding as leading silence before the first clip
                if not first_clip_added:
                    first_clip_added = True
                    padding_s = self.config.get_modifier("first_line_padding_s")
                    if padding_s > 0:
                        padding_ms = int(padding_s * 1000)
                        timeline.append({
                            "type": "silence",
                            "duration_ms": padding_ms,
                            "start_ms": current_ms,
                        })
                        current_ms += padding_ms

                duration_ms = _get_audio_duration_ms(clip_path)
                timeline.append({
                    "type": "clip",
                    "path": str(clip_path),
                    "line": line,
                    "start_ms": current_ms,
                    "duration_ms": duration_ms,
                })
                current_ms += duration_ms

                # Calculate pause after this dialogue line.
                # is_last is True only when this dialogue line is the final active event
                # in the whole script (nothing follows it — no SFX, no explicit pause).
                dialogue_idx = dialogue_lines.index(line)
                next_dialogue = dialogue_lines[dialogue_idx + 1] if dialogue_idx + 1 < dialogue_count else None
                is_first = (dialogue_idx == 0)
                is_last = (last_active is line)

                pause_s = self.calculate_pause_after(line, next_dialogue, is_first, is_last)
                if pause_s > 0:
                    pause_ms = int(pause_s * 1000)
                    timeline.append({
                        "type": "silence",
                        "duration_ms": pause_ms,
                        "start_ms": current_ms,
                    })
                    current_ms += pause_ms

            elif line.line_type == "pause":
                pause_ms = int(line.pause_duration * 1000)
                timeline.append({
                    "type": "silence",
                    "duration_ms": pause_ms,
                    "start_ms": current_ms,
                })
                current_ms += pause_ms

            elif line.line_type == "play_command" and line.play_command:
                cmd = line.play_command
                if cmd.command == "play":
                    resolved_path = sfx_paths.get(cmd.filename, "")
                    timeline.append({
                        "type": "sfx",
                        "path": resolved_path,
                        "filename": cmd.filename,
                        "channel": cmd.channel,
                        "mode": cmd.mode,
                        "start_ms": current_ms,
                    })
                elif cmd.command == "stop":
                    timeline.append({
                        "type": "sfx_stop",
                        "channel": cmd.channel,
                        "start_ms": current_ms,
                    })

        return timeline

    def merge_clips(self, timeline, output_pure, output_loudnorm, sfx_paths=None,
                    output_format: str = "mp3"):
        """
        Execute the merge using ffmpeg.
        Produces both a pure (no normalization) and loudnorm version.

        Pass 1: Concatenate all dialogue clips + silence into base audio.
        Pass 2: Overlay SFX tracks onto the base using adelay + amix.
        Pass 3: Peak-normalize the pure output so its volume is comparable to the loudnorm version.

        Args:
            timeline: List of timeline events from build_timeline()
            output_pure: Path for the pure merged output
            output_loudnorm: Path for the loudnorm merged output
            sfx_paths: Dict mapping sfx filename -> resolved file path (unused here;
                       paths are already embedded in timeline events by build_timeline)

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        concat_entries = []
        for event in timeline:
            if event["type"] == "clip":
                concat_entries.append(("file", event["path"]))
            elif event["type"] == "silence":
                concat_entries.append(("silence", event["duration_ms"]))

        if not concat_entries:
            return False, "No audio clips to merge."

        ext = ".ogg" if output_format == "ogg" else ".mp3"

        try:
            # Pass 1: Concatenate dialogue clips into base audio
            success, error = self._merge_with_filter_complex(
                concat_entries, str(output_pure), ext
            )
            if not success:
                return False, error

            # Pass 2: Overlay SFX tracks onto the base (if any)
            sfx_events = [e for e in timeline if e["type"] == "sfx" and e.get("path") and Path(e["path"]).exists()]
            if sfx_events:
                stop_events = [e for e in timeline if e["type"] == "sfx_stop"]
                base_duration_ms = _get_audio_duration_ms(str(output_pure))

                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp_path = tmp.name

                success, error = self._overlay_sfx_tracks(
                    sfx_events, stop_events, str(output_pure),
                    tmp_path, base_duration_ms
                )
                if success:
                    # Replace pure output with the SFX-mixed version
                    import os
                    os.replace(tmp_path, str(output_pure))
                else:
                    # SFX overlay failed — log-worthy but don't abort; pure stays dialogue-only
                    try:
                        import os
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                    # Return the error so the caller can surface it
                    return False, error

            # Always peak-normalize the pure output in-place
            success, error = self._apply_peak_normalize(str(output_pure))
            if not success:
                return False, error

            success, error = self._apply_loudnorm(str(output_pure), str(output_loudnorm))
            if not success:
                return False, error

            return True, None

        except Exception as e:
            return False, f"Merge failed: {str(e)}"

    def _overlay_sfx_tracks(self, sfx_events, stop_events, base_path, output_path, base_duration_ms):
        """
        Mix SFX tracks onto an already-merged base audio file using FFMPEG filter_complex.

        Each SFX play event is delayed to its start_ms position. Loop-mode SFX are
        looped and trimmed to their active duration (until the matching {stop} event
        or end of the base audio). Once-mode SFX play exactly once from their start_ms.

        Args:
            sfx_events: List of timeline events with type="sfx" and valid paths
            stop_events: List of timeline events with type="sfx_stop"
            base_path: Path to the base merged audio (dialogue-only)
            output_path: Path for the mixed output
            base_duration_ms: Duration of base audio in milliseconds

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        startupinfo = _get_subprocess_startupinfo()

        # Build inputs: base audio is input 0, each SFX file is a subsequent input
        cmd = ["ffmpeg", "-i", str(base_path)]
        for event in sfx_events:
            cmd.extend(["-i", str(event["path"])])

        filter_parts = []
        sfx_labels = []

        for idx, event in enumerate(sfx_events):
            input_idx = idx + 1  # base is 0
            start_ms = event["start_ms"]
            channel = event["channel"]
            mode = event["mode"]

            # Determine the end time for this SFX track
            if mode == "loop":
                # Find the earliest matching {stop} event for this channel after start_ms
                end_ms = base_duration_ms
                for stop in stop_events:
                    stop_channel = stop["channel"]
                    if stop_channel == channel or stop_channel == "all":
                        if stop["start_ms"] > start_ms:
                            end_ms = stop["start_ms"]
                            break
                active_duration_s = max(0.0, (end_ms - start_ms) / 1000.0)

                # Loop infinitely, trim to active duration, then delay to start position
                label = f"[sfx{idx}]"
                # aloop: loop=-1 means infinite, size needs to be large enough to cover
                # any realistic clip length (2e+09 samples at 44100Hz is ~12 hours)
                filter_parts.append(
                    f"[{input_idx}:a]"
                    f"aloop=loop=-1:size=2000000000,"
                    f"atrim=0:{active_duration_s:.3f},"
                    f"adelay={start_ms}|{start_ms}"
                    f"{label}"
                )
            else:
                # Once mode: just delay to start position, plays naturally to its end
                label = f"[sfx{idx}]"
                filter_parts.append(
                    f"[{input_idx}:a]"
                    f"adelay={start_ms}|{start_ms}"
                    f"{label}"
                )

            sfx_labels.append(label)

        # Mix all streams: base [0:a] + all sfx labels.
        # normalize=0 disables amix's automatic volume compensation (which divides
        # by the number of active inputs and shifts volume as streams drop out),
        # so the base audio plays at its original level with SFX added on top.
        all_inputs = "[0:a]" + "".join(sfx_labels)
        n_inputs = 1 + len(sfx_labels)
        filter_parts.append(
            f"{all_inputs}amix=inputs={n_inputs}:duration=longest:dropout_transition=0:normalize=0[out]"
        )

        filter_graph = ";".join(filter_parts)
        cmd.extend(["-filter_complex", filter_graph])
        cmd.extend(["-map", "[out]", "-y", output_path])

        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True,
                           startupinfo=startupinfo)
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"FFmpeg SFX overlay failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."

    def _merge_with_filter_complex(self, concat_entries, output_path, ext=".mp3"):
        """Merge clips with silence gaps using the ffmpeg concat demuxer.

        Writes the file list to a temp file instead of passing every clip as a
        CLI argument, so the command length is always short regardless of how
        many clips the script contains. Avoids the Windows ~32KB command-line
        length limit that would break large scripts with filter_complex -i flags.
        """
        if not any(t == "file" for t, _ in concat_entries):
            return False, "No audio clips to merge."

        startupinfo = _get_subprocess_startupinfo()
        tmpdir = tempfile.mkdtemp(prefix="svtg_merge_")
        try:
            # Pre-generate silence files — one per unique duration, reused
            # across duplicates (most scripts repeat the same pause lengths many
            # times, so this typically produces only a handful of silence files).
            silence_cache = {}

            def get_silence_file(duration_ms):
                if duration_ms in silence_cache:
                    return silence_cache[duration_ms]
                sil_path = os.path.join(tmpdir, f"sil_{duration_ms}{ext}")
                subprocess.run([
                    "ffmpeg", "-f", "lavfi",
                    "-i", "anullsrc=r=48000:cl=mono",
                    "-t", str(duration_ms / 1000.0),
                    "-y", sil_path
                ], check=True, capture_output=True, startupinfo=startupinfo)
                silence_cache[duration_ms] = sil_path
                return sil_path

            # Write the concat demuxer list file — all segments go here, not on
            # the command line, so the command stays short no matter the script size.
            list_path = os.path.join(tmpdir, "concat_list.txt")
            with open(list_path, "w", encoding="utf-8") as f:
                for entry_type, value in concat_entries:
                    if entry_type == "file":
                        safe = Path(value).as_posix().replace("'", "\\'")
                        f.write(f"file '{safe}'\n")
                    elif entry_type == "silence":
                        sil = get_silence_file(value)
                        safe = Path(sil).as_posix().replace("'", "\\'")
                        f.write(f"file '{safe}'\n")

            subprocess.run([
                "ffmpeg", "-f", "concat", "-safe", "0",
                "-i", list_path,
                "-ar", "48000",
                "-y", output_path
            ], check=True, capture_output=True, text=True, startupinfo=startupinfo)
            return True, None

        except subprocess.CalledProcessError as e:
            return False, f"FFmpeg merge failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _apply_peak_normalize(self, filepath):
        """Peak-normalize an audio file in-place (overwrites the file).

        Two-pass approach matching Tenacity's "Normalize" default behavior:
        Pass 1: Measure the true peak level using volumedetect.
        Pass 2: Apply a linear gain so the peak reaches exactly 0 dBFS.
        Dynamics and relative levels are completely preserved.
        """
        startupinfo = _get_subprocess_startupinfo()
        try:
            # Pass 1: Measure peak
            result = subprocess.run([
                "ffmpeg", "-i", filepath,
                "-af", "volumedetect",
                "-f", "null", "-"
            ], capture_output=True, text=True, startupinfo=startupinfo)

            # volumedetect writes to stderr; parse max_volume
            import re
            match = re.search(r"max_volume:\s*([-\d.]+)\s*dB", result.stderr)
            if not match:
                return False, "Peak normalize failed: could not read max_volume from ffmpeg output."

            max_volume_db = float(match.group(1))
            # If already at 0dBFS, nothing to do
            if max_volume_db >= 0.0:
                return True, None

            # Gain needed to bring peak to 0dBFS
            gain_db = -max_volume_db

            # Pass 2: Apply linear gain
            file_ext = Path(filepath).suffix or ".mp3"
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp:
                tmp_path = tmp.name

            subprocess.run([
                "ffmpeg", "-i", filepath,
                "-af", f"volume={gain_db}dB",
                "-y", tmp_path
            ], check=True, capture_output=True, text=True, startupinfo=startupinfo)

            os.replace(tmp_path, filepath)
            return True, None
        except subprocess.CalledProcessError as e:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            return False, f"Peak normalize failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."

    def _apply_loudnorm(self, input_path, output_path):
        """Apply loudness normalization to create the balanced version."""
        try:
            subprocess.run([
                "ffmpeg", "-i", input_path,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                "-y", output_path
            ], check=True, capture_output=True, text=True,
               startupinfo=_get_subprocess_startupinfo())
            return True, None
        except subprocess.CalledProcessError as e:
            return False, f"Loudnorm failed: {e.stderr}"
        except FileNotFoundError:
            return False, "FFMPEG not found in PATH."
