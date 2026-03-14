"""
Tab 2 state and event-handling methods (mixin).
Extracted from gui_tab2.py to keep file sizes manageable.
All methods here are mixed into ScriptToVoiceGUI via Tab2StateMixin.
"""

import tkinter as tk
from config import AUDIO_EFFECTS, FFMPEG_PITCH_SEMITONES_DEFAULT
from pathlib import Path


class Tab2StateMixin:
    """Mixin: data/event methods for Tab 2 (Voice Settings)"""

    def _create_speaker_vars(self, speaker_id, profile):
        """Create tkinter variables for a speaker, initialized from profile."""
        vars_dict = {}

        vars_dict["voice"] = tk.StringVar(value=profile.voice)
        vars_dict["pitch_semitones"] = tk.DoubleVar(value=profile.pitch_semitones)
        vars_dict["speaking_rate"] = tk.DoubleVar(value=profile.speaking_rate)
        vars_dict["yell_impact_percent"] = tk.IntVar(value=profile.yell_impact_percent)
        vars_dict["volume_percent"] = tk.IntVar(value=profile.volume_percent)

        for effect_name in AUDIO_EFFECTS:
            if effect_name == "pitch_shift":
                vars_dict[effect_name] = tk.DoubleVar(
                    value=getattr(profile, "pitch_shift_semitones", FFMPEG_PITCH_SEMITONES_DEFAULT))
            else:
                vars_dict[effect_name] = tk.StringVar(value=getattr(profile, effect_name, "off"))

        vars_dict["fmsu"] = tk.BooleanVar(value=profile.fmsu)
        vars_dict["reverse"] = tk.BooleanVar(value=profile.reverse)

        # Trace all variables to auto-save on change
        for var_name, var in vars_dict.items():
            var.trace_add("write", lambda *args, sid=speaker_id: self._on_speaker_var_changed(sid))

        return vars_dict

    def _on_speaker_var_changed(self, speaker_id):
        """Auto-save speaker settings to character profiles on any change."""
        if speaker_id not in self._speaker_vars:
            return

        vars_dict = self._speaker_vars[speaker_id]
        profile = self.char_profiles.get_or_create_profile(speaker_id)

        # Read voice - extract short name from display string
        voice_val = vars_dict["voice"].get()
        if " | " in voice_val:
            profile.voice = voice_val.split(" | ")[0]
        elif voice_val:
            profile.voice = voice_val

        profile.pitch_semitones = vars_dict["pitch_semitones"].get()
        profile.speaking_rate = vars_dict["speaking_rate"].get()
        profile.yell_impact_percent = vars_dict["yell_impact_percent"].get()
        profile.volume_percent = vars_dict["volume_percent"].get()

        for effect_name in AUDIO_EFFECTS:
            if effect_name == "pitch_shift":
                profile.pitch_shift_semitones = vars_dict[effect_name].get()
            else:
                setattr(profile, effect_name, vars_dict[effect_name].get())

        profile.fmsu = vars_dict["fmsu"].get()
        profile.reverse = vars_dict["reverse"].get()

        self.char_profiles.update_profile(speaker_id, profile)

        if hasattr(self, '_summary_status_label'):
            self._summary_status_label.config(text="Summary outdated — click Refresh",
                                              foreground="#FFD43B")

    def _set_voices_on_comboboxes(self):
        """Populate voice comboboxes for all speakers once voices are loaded."""
        for speaker_id, widgets in self._speaker_widgets.items():
            combo = widgets.get("voice_combo")
            if combo:
                combo["values"] = self._available_voices

                # Try to select the matching voice
                vars_dict = self._speaker_vars[speaker_id]
                current_voice = vars_dict["voice"].get()

                # Find matching display string
                for voice_display in self._available_voices:
                    short_name = voice_display.split(" | ")[0]
                    if short_name == current_voice:
                        vars_dict["voice"].set(voice_display)
                        break

    def _populate_sfx_list(self, sound_effects):
        """Populate the SFX file list from parse results."""
        from ttkbootstrap.constants import LEFT
        import ttkbootstrap as ttk

        try:
            from ttkbootstrap.tooltip import ToolTip
            _tip_avail = True
        except ImportError:
            _tip_avail = False

        def _tip(widget, text):
            if _tip_avail and widget:
                ToolTip(widget, text=text, delay=400)

        # Clear existing
        for widget in self._sfx_list_frame.winfo_children():
            widget.destroy()
        self._sfx_check_vars = {}
        self._sfx_status_labels = {}

        if not sound_effects:
            ttk.Label(self._sfx_list_frame,
                     text="No sound effects referenced in this script.",
                     font=("Consolas", 9, "italic"),
                     foreground="#74C0FC").pack(pady=5)
            return

        # Header row with select-all checkbox
        header = ttk.Frame(self._sfx_list_frame)
        header.pack(fill="x", pady=(0, 3))

        self._sfx_all_var = tk.BooleanVar(value=True)
        sfx_all_cb = ttk.Checkbutton(header, text="Apply effects to all SFX",
                                     variable=self._sfx_all_var,
                                     command=self._on_sfx_all_toggled)
        sfx_all_cb.pack(side=LEFT)
        _tip(sfx_all_cb, "Toggle whether FFMPEG audio effects (set below) are applied to all SFX files.\n"
                         "Unchecking means SFX will be included in the output as-is, with no effects.")

        ttk.Label(header, text=f"({len(sound_effects)} file(s))",
                 font=("Consolas", 9), foreground="#8AAAC8").pack(side=LEFT, padx=(5, 0))

        # Individual SFX rows
        for sfx in sound_effects:
            row = ttk.Frame(self._sfx_list_frame)
            row.pack(fill="x", pady=1)

            check_var = tk.BooleanVar(value=True)
            check_var.trace_add("write", lambda *_: self._on_sfx_settings_changed())
            self._sfx_check_vars[sfx.filename] = check_var

            sfx_cb = ttk.Checkbutton(row, text=sfx.filename,
                                     variable=check_var)
            sfx_cb.pack(side=LEFT, padx=(20, 10))
            _tip(sfx_cb, f"Apply FFMPEG effects to {sfx.filename} during generation.\n"
                         "Uncheck to use this SFX file as-is, without any effects.")

            lines_str = ", ".join(str(ln) for ln in sfx.line_numbers)
            ttk.Label(row, text=f"(lines: {lines_str})",
                     font=("Consolas", 8), foreground="#8AAAC8").pack(side=LEFT, padx=(0, 10))

            status_label = ttk.Label(row, text="not scanned",
                                    font=("Consolas", 8, "italic"),
                                    foreground="#74C0FC")
            status_label.pack(side=LEFT)
            self._sfx_status_labels[sfx.filename] = status_label

    def _on_sfx_settings_changed(self):
        """Mark the generation summary as outdated when any SFX setting changes."""
        if hasattr(self, '_summary_status_label'):
            self._summary_status_label.config(text="Summary outdated — click Refresh",
                                              foreground="#FFD43B")

    def _on_sfx_all_toggled(self):
        """Handle the 'select all' SFX checkbox toggle."""
        new_val = self._sfx_all_var.get()
        for var in self._sfx_check_vars.values():
            var.set(new_val)
        self._on_sfx_settings_changed()

    def _on_sfx_subfolder_changed(self):
        """Re-scan SFX folder when subfolder checkbox changes."""
        folder = self._sfx_folder_var.get()
        if folder:
            self._scan_sfx_folder(folder)

    def _scan_sfx_folder(self, folder_path):
        """Scan the SFX folder and update status labels."""
        from file_manager import FileManager

        required = list(self._sfx_check_vars.keys())
        if not required:
            return

        search_subs = self._sfx_subfolders_var.get()
        results = FileManager.scan_sfx_folder(folder_path, required, search_subs)

        found_count = 0
        for filename, found_path in results.items():
            label = self._sfx_status_labels.get(filename)
            if not label:
                continue

            if found_path:
                label.config(text="Found", foreground="#69DB7C")
                found_count += 1
                # Update SFX event with found path
                if hasattr(self, '_last_parse_result') and self._last_parse_result:
                    for sfx in self._last_parse_result.sound_effects:
                        if sfx.filename == filename:
                            sfx.found = True
                            sfx.found_path = found_path
            else:
                label.config(text="Missing", foreground="#FF6B6B")

        total = len(required)
        if hasattr(self, 'status_label'):
            self.status_label.config(
                text=f"SFX scan: {found_count}/{total} files found")
