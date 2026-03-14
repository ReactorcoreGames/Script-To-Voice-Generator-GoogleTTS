"""
Tab 3: Generation & Output
For Script to Voice Generator GUI.
Summary display, project name input, output folder picker,
generate button with progress bar and scrolling log.
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from config import MAX_PROJECT_NAME_LENGTH, INVALID_FILENAME_CHARS, AUDIO_EFFECTS


class Tab3Builder:
    """Mixin class for building Tab 3 (Generation) UI"""

    def build_tab3(self, parent):
        """Build the complete Tab 3 interface."""
        # State
        self._gen_project_name_var = tk.StringVar(value="")
        self._gen_output_folder_var = tk.StringVar(value="")
        saved_subfolder_pref = self.config_manager.get_ui("use_project_subfolder")
        _subfolder_default = saved_subfolder_pref if isinstance(saved_subfolder_pref, bool) else True
        self._gen_use_project_subfolder_var = tk.BooleanVar(value=_subfolder_default)
        self._gen_use_project_subfolder_var.trace_add(
            "write",
            lambda *_: self.config_manager.set_ui(
                "use_project_subfolder", self._gen_use_project_subfolder_var.get()
            )
        )
        self._gen_progress_var = tk.DoubleVar(value=0.0)
        self._gen_running = False
        self._gen_cancel_requested = False

        # Main scrollable container
        canvas = ttk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas, padding=15)

        scrollable.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.bind("<Configure>",
                   lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel scrolling — forward from any child widget up to canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def bind_mousewheel_tab3(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel_tab3(child)

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)
        self._tab3_bind_mousewheel = bind_mousewheel_tab3

        # Title
        ttk.Label(scrollable, text="Generate Output",
                 font=("Consolas", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(scrollable,
                 text="Review the summary, set a project name and output folder, then generate.",
                 font=("Consolas", 10), wraplength=900, justify="center").pack(pady=(0, 15))

        # --- Summary Section ---
        self._build_summary_section(scrollable)

        # --- Project Configuration ---
        self._build_project_config_section(scrollable)

        # --- Generation Controls ---
        self._build_generation_controls(scrollable)

        # --- Generation Log ---
        self._build_generation_log(scrollable)

        # Bind mousewheel to all child widgets
        bind_mousewheel_tab3(scrollable)

    def _build_summary_section(self, parent):
        """Build the generation summary display."""
        frame = ttk.LabelFrame(parent, text="Generation Summary", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        summary_container = ttk.Frame(frame)
        summary_container.pack(fill=X)

        summary_scrollbar = ttk.Scrollbar(summary_container, orient="vertical")
        self._summary_text = tk.Text(summary_container, height=12, wrap="word",
                                     font=("Consolas", 10),
                                     bg="#141824", fg="#C8D8F0",
                                     relief="flat", borderwidth=1,
                                     state="disabled",
                                     selectbackground="#2A3A5C",
                                     yscrollcommand=summary_scrollbar.set)
        summary_scrollbar.config(command=self._summary_text.yview)
        self._summary_text.pack(side=LEFT, fill=X, expand=True)
        summary_scrollbar.pack(side=RIGHT, fill=Y)

        # Configure tags for colored text
        self._summary_text.tag_configure("header", foreground="#60CDFF",
                                         font=("Consolas", 10, "bold"))
        self._summary_text.tag_configure("speaker", foreground="#69DB7C")
        self._summary_text.tag_configure("sfx", foreground="#74C0FC")
        self._summary_text.tag_configure("warning", foreground="#FFD43B")

        # Compact usage line
        from config import GOOGLE_TTS_FREE_TIER_CHARS
        usage_row = ttk.Frame(frame)
        usage_row.pack(anchor=W, pady=(5, 0))

        ttk.Label(usage_row, text="API usage this month:",
                  font=("Consolas", 9), foreground="#8AAAC8").pack(side=LEFT, padx=(0, 4))
        self._tab3_usage_var = tk.StringVar(value="—")
        ttk.Label(usage_row, textvariable=self._tab3_usage_var,
                  font=("Consolas", 9), foreground="#74C0FC").pack(side=LEFT)

        # Refresh button + stale indicator
        refresh_row = ttk.Frame(frame)
        refresh_row.pack(anchor=W, pady=(3, 0))

        ttk.Button(refresh_row, text="Refresh Summary",
                  command=self._refresh_summary,
                  bootstyle=INFO, width=18).pack(side=LEFT, padx=(0, 10))

        self._summary_status_label = ttk.Label(refresh_row, text="",
                                               font=("Consolas", 9))
        self._summary_status_label.pack(side=LEFT)

    def _build_project_config_section(self, parent):
        """Build project name and output folder configuration."""
        frame = ttk.LabelFrame(parent, text="Project Configuration", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        # Project name row
        name_row = ttk.Frame(frame)
        name_row.pack(fill=X, pady=(0, 8))

        ttk.Label(name_row, text="Project Name:",
                 font=("Consolas", 10, "bold")).pack(side=LEFT, padx=(0, 5))

        name_entry = ttk.Entry(name_row, textvariable=self._gen_project_name_var,
                               width=30, font=("Consolas", 10))
        name_entry.pack(side=LEFT, padx=(0, 5))

        self._project_name_status = ttk.Label(name_row, text="",
                                              font=("Consolas", 9))
        self._project_name_status.pack(side=LEFT, padx=(5, 0))

        ttk.Label(name_row, text=f"(max {MAX_PROJECT_NAME_LENGTH} chars, no special characters)",
                 font=("Consolas", 9), foreground="#8AAAC8").pack(side=LEFT, padx=(10, 0))

        # Validate project name in real-time
        self._gen_project_name_var.trace_add("write", self._on_project_name_changed)

        # Output folder row
        folder_row = ttk.Frame(frame)
        folder_row.pack(fill=X, pady=(0, 0))

        ttk.Label(folder_row, text="Output Folder:",
                 font=("Consolas", 10, "bold")).pack(side=LEFT, padx=(0, 5))

        self._output_folder_entry = ttk.Entry(folder_row,
                                               textvariable=self._gen_output_folder_var,
                                               width=50, state="readonly",
                                               font=("Consolas", 9))
        self._output_folder_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        ttk.Button(folder_row, text="Browse...",
                  command=self._on_pick_output_folder,
                  bootstyle=INFO, width=10).pack(side=LEFT)

        # Subfolder checkbox
        subfolder_row = ttk.Frame(frame)
        subfolder_row.pack(fill=X, pady=(6, 0))

        ttk.Checkbutton(subfolder_row,
                        text="Save into project subfolder  (creates  output_folder/project_name/)",
                        variable=self._gen_use_project_subfolder_var,
                        bootstyle="secondary").pack(side=LEFT)

    def _build_generation_controls(self, parent):
        """Build generate/cancel buttons and progress bar."""
        frame = ttk.LabelFrame(parent, text="Generation", padding=10)
        frame.pack(fill=X, pady=(0, 10))

        # Buttons row
        btn_row = ttk.Frame(frame)
        btn_row.pack(fill=X, pady=(0, 8))

        self._btn_generate = ttk.Button(btn_row, text="Generate All",
                                        command=self._on_generate_clicked,
                                        bootstyle=SUCCESS, width=20)
        self._btn_generate.pack(side=LEFT, padx=(0, 10))

        self._btn_cancel = ttk.Button(btn_row, text="Cancel",
                                      command=self._on_cancel_clicked,
                                      bootstyle=DANGER, width=12,
                                      state="disabled")
        self._btn_cancel.pack(side=LEFT, padx=(0, 10))

        self._btn_open_output = ttk.Button(btn_row, text="Open Output Folder",
                                           command=self._on_open_output_folder,
                                           bootstyle=INFO, width=20,
                                           state="disabled")
        self._btn_open_output.pack(side=RIGHT)

        # Progress bar
        self._progress_bar = ttk.Progressbar(frame, variable=self._gen_progress_var,
                                              maximum=100, mode="determinate",
                                              bootstyle=SUCCESS)
        self._progress_bar.pack(fill=X, pady=(0, 3))

        # Progress label
        self._progress_label = ttk.Label(frame, text="Ready",
                                         font=("Consolas", 9),
                                         foreground="#8AAAC8")
        self._progress_label.pack(anchor=W)

    def _build_generation_log(self, parent):
        """Build the scrolling generation log."""
        frame = ttk.LabelFrame(parent, text="Generation Log", padding=10)
        frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        log_container = ttk.Frame(frame)
        log_container.pack(fill=BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(log_container, orient="vertical")
        self._gen_log = tk.Text(log_container, height=15, wrap="word",
                                font=("Consolas", 9),
                                bg="#141824", fg="#C8D8F0",
                                relief="flat", borderwidth=1,
                                state="disabled",
                                yscrollcommand=log_scrollbar.set,
                                selectbackground="#2A3A5C")
        log_scrollbar.config(command=self._gen_log.yview)

        self._gen_log.pack(side=LEFT, fill=BOTH, expand=True)
        log_scrollbar.pack(side=RIGHT, fill=Y)

        # Configure tags for log colors
        self._gen_log.tag_configure("error", foreground="#FF6B6B")
        self._gen_log.tag_configure("success", foreground="#69DB7C")
        self._gen_log.tag_configure("info", foreground="#74C0FC")
        self._gen_log.tag_configure("warning", foreground="#FFD43B")
        self._gen_log.tag_configure("header", foreground="#60CDFF",
                                    font=("Consolas", 9, "bold"))

    # ── Summary helpers ──────────────────────────────────────

    def _refresh_tab3_usage(self):
        """Update the compact usage label from config_manager."""
        from config import GOOGLE_TTS_FREE_TIER_CHARS
        if not hasattr(self, '_tab3_usage_var'):
            return
        try:
            used = self.config_manager.get_char_usage()
            self._tab3_usage_var.set(f"~{used:,} / {GOOGLE_TTS_FREE_TIER_CHARS:,} chars")
        except Exception:
            pass

    def _refresh_summary(self):
        """Refresh the generation summary from current parse result."""
        self._refresh_tab3_usage()
        self._summary_text.config(state="normal")
        self._summary_text.delete("1.0", "end")

        result = getattr(self, '_last_parse_result', None)
        if not result or not result.speakers:
            self._summary_text.insert("end", "No script loaded.\n", "warning")
            self._summary_text.insert("end",
                                      "Go to Tab 1 to load a script, then Tab 2 to configure voices.")
            self._summary_text.config(state="disabled")
            if hasattr(self, '_summary_status_label'):
                self._summary_status_label.config(text="No script loaded", foreground="#FFD43B")
            return

        # Header
        title = result.title or "(untitled)"
        self._summary_text.insert("end", f"Script: {title}\n", "header")
        self._summary_text.insert("end", "=" * 50 + "\n")

        # Line counts
        self._summary_text.insert("end",
                                  f"Total dialogue lines: {result.total_dialogue_lines}\n")
        self._summary_text.insert("end",
                                  f"Total speakers: {len(result.speakers)}\n\n")

        # Speaker details
        self._summary_text.insert("end", "Speakers:\n", "header")
        for speaker_id in result.speakers:
            effects_str = self._get_speaker_effects_summary(speaker_id)
            self._summary_text.insert("end", f"  {speaker_id}", "speaker")
            if effects_str:
                self._summary_text.insert("end", f"  ({effects_str})")
            self._summary_text.insert("end", "\n")

        # SFX
        if result.sound_effects:
            self._summary_text.insert("end",
                                      f"\nSound effects: {len(result.sound_effects)} file(s)\n",
                                      "sfx")
            for sfx in result.sound_effects:
                included = self._sfx_check_vars.get(sfx.filename)
                if included is not None and not included.get():
                    status = "skipped"
                elif sfx.found:
                    status = "found"
                else:
                    status = "missing"
                self._summary_text.insert("end", f"  - {sfx.filename} ({status})\n", "sfx")

            # SFX effects summary
            sfx_effects_summary = self._get_sfx_effects_summary()
            if sfx_effects_summary:
                self._summary_text.insert("end",
                                          f"  Effects on SFX: {sfx_effects_summary}\n", "sfx")
            else:
                self._summary_text.insert("end", "  Effects on SFX: none (raw files)\n", "sfx")

        self._summary_text.insert("end", "\n" + "=" * 50)
        self._summary_text.config(state="disabled")

        if hasattr(self, '_summary_status_label'):
            self._summary_status_label.config(text="Up to date", foreground="#69DB7C")

        # Load persisted project name / output folder from config
        saved_name = self.config_manager.get_ui("last_project_name")
        if saved_name and not self._gen_project_name_var.get():
            self._gen_project_name_var.set(saved_name)

        saved_folder = self.config_manager.get_ui("last_output_folder")
        if saved_folder and not self._gen_output_folder_var.get():
            self._gen_output_folder_var.set(saved_folder)

    def _get_sfx_effects_summary(self):
        """Get a short summary of active effects applied to SFX files."""
        sfx_effect_vars = getattr(self, '_sfx_effect_vars', {})
        active = []
        for effect_name in AUDIO_EFFECTS:
            var = sfx_effect_vars.get(effect_name)
            if not var:
                continue
            val = var.get()
            if effect_name == "pitch_shift":
                if isinstance(val, float) and val != 0.0:
                    active.append(f"Pitch Shift: {val:+.1f} st")
            elif val != "off":
                short = AUDIO_EFFECTS[effect_name]["name"]
                active.append(f"{short}: {val}")
        for attr, label in (("_sfx_fmsu_var", "FMSU"), ("_sfx_reverse_var", "Reverse")):
            var = getattr(self, attr, None)
            if var and var.get():
                active.append(label)
        return ", ".join(active) if active else ""

    def _get_speaker_effects_summary(self, speaker_id):
        """Get a short summary of active effects for a speaker."""
        vars_dict = self._speaker_vars.get(speaker_id, {})
        if not vars_dict:
            return ""

        active = []
        for effect_name in AUDIO_EFFECTS:
            val = vars_dict.get(effect_name)
            if val and val.get() != "off":
                short = AUDIO_EFFECTS[effect_name]["name"]
                active.append(f"{short}: {val.get()}")

        for flag_name, label in (("fmsu", "FMSU"), ("reverse", "Reverse")):
            val = vars_dict.get(flag_name)
            if val and val.get():
                active.append(label)

        return ", ".join(active) if active else "clean"

    # ── Project name validation ──────────────────────────────

    def _on_project_name_changed(self, *args):
        """Validate project name in real-time."""
        name = self._gen_project_name_var.get()

        if not name:
            self._project_name_status.config(text="", foreground="#8AAAC8")
            return

        # Check length
        if len(name) > MAX_PROJECT_NAME_LENGTH:
            self._project_name_status.config(
                text=f"Too long ({len(name)}/{MAX_PROJECT_NAME_LENGTH})",
                foreground="#FF6B6B")
            return

        # Check for invalid characters
        bad_chars = [ch for ch in name if ch in INVALID_FILENAME_CHARS]
        if bad_chars:
            self._project_name_status.config(
                text=f"Invalid chars: {', '.join(repr(c) for c in bad_chars)}",
                foreground="#FF6B6B")
            return

        self._project_name_status.config(
            text=f"OK ({len(name)}/{MAX_PROJECT_NAME_LENGTH})",
            foreground="#69DB7C")

    # ── Generation log helpers ───────────────────────────────

    def gen_log(self, message, tag=None):
        """Append a message to the generation log."""
        self._gen_log.config(state="normal")
        if tag:
            self._gen_log.insert("end", message + "\n", tag)
        else:
            self._gen_log.insert("end", message + "\n")
        self._gen_log.see("end")
        self._gen_log.config(state="disabled")
        self.root.update_idletasks()

    def gen_log_clear(self):
        """Clear the generation log."""
        self._gen_log.config(state="normal")
        self._gen_log.delete("1.0", "end")
        self._gen_log.config(state="disabled")

    def gen_progress(self, value, label_text=None):
        """Update generation progress bar and label."""
        self._gen_progress_var.set(value)
        if label_text:
            self._progress_label.config(text=label_text)
        self.root.update_idletasks()
