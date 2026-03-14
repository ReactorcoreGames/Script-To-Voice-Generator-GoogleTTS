"""
Tab 1: Script Loading and Validation
For Script to Voice Generator GUI
"""

import tkinter as tk
from tkinter import scrolledtext
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from config import APP_THEME


class Tab1Builder:
    """Mixin class for building Tab 1 (Script Loading) UI"""

    def build_tab1(self, parent):
        """Build the complete Tab 1 interface"""
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

        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)

        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable.bind("<MouseWheel>", on_mousewheel)

        self._tab1_canvas = canvas
        self._tab1_bind_mousewheel = bind_mousewheel

        # --- Title ---
        title_label = ttk.Label(scrollable, text="Load Script File",
                               font=("Consolas", 18, "bold"))
        title_label.pack(pady=(0, 5))

        desc_label = ttk.Label(scrollable,
                              text="Load a formatted script file (.txt or .md) to extract "
                                   "speakers, dialogue, and sound effects.",
                              wraplength=900, justify="center",
                              font=("Consolas", 10))
        desc_label.pack(pady=(0, 15))

        # --- File Loading Section ---
        file_frame = ttk.LabelFrame(scrollable, text="Script File", padding=10)
        file_frame.pack(fill=X, pady=(0, 10))

        btn_row = ttk.Frame(file_frame)
        btn_row.pack(fill=X, pady=5)

        self.btn_load_script = ttk.Button(btn_row, text="Open Script File...",
                                          command=self.on_load_script,
                                          bootstyle=PRIMARY, width=22)
        self.btn_load_script.pack(side=LEFT, padx=(0, 10))

        self.btn_reload_script = ttk.Button(btn_row, text="Reload Script",
                                            command=self.on_reload_script,
                                            bootstyle=INFO, width=16,
                                            state="disabled")
        self.btn_reload_script.pack(side=LEFT, padx=(0, 10))

        self.btn_open_script_folder = ttk.Button(btn_row, text="Open Script Folder",
                                                  command=self.on_open_script_folder,
                                                  bootstyle=SECONDARY, width=20,
                                                  state="disabled")
        self.btn_open_script_folder.pack(side=LEFT, padx=(0, 10))

        self.loaded_file_label = ttk.Label(file_frame, text="No file loaded",
                                          font=("Consolas", 9),
                                          foreground="#74C0FC")
        self.loaded_file_label.pack(anchor=W, pady=(0, 5))

        # --- Parse Results / Stats ---
        stats_frame = ttk.LabelFrame(scrollable, text="Script Summary", padding=10)
        stats_frame.pack(fill=X, pady=(0, 10))

        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=X)

        # Row 1: Dialogue lines and speakers
        ttk.Label(stats_grid, text="Dialogue lines:",
                 font=("Consolas", 10, "bold")).grid(row=0, column=0, sticky=W, padx=(0, 5))
        self.stat_lines = ttk.Label(stats_grid, text="--",
                                   font=("Consolas", 10))
        self.stat_lines.grid(row=0, column=1, sticky=W, padx=(0, 30))

        ttk.Label(stats_grid, text="Unique speakers:",
                 font=("Consolas", 10, "bold")).grid(row=0, column=2, sticky=W, padx=(0, 5))
        self.stat_speakers = ttk.Label(stats_grid, text="--",
                                      font=("Consolas", 10))
        self.stat_speakers.grid(row=0, column=3, sticky=W, padx=(0, 30))

        ttk.Label(stats_grid, text="Sound effects:",
                 font=("Consolas", 10, "bold")).grid(row=0, column=4, sticky=W, padx=(0, 5))
        self.stat_sfx = ttk.Label(stats_grid, text="--",
                                 font=("Consolas", 10))
        self.stat_sfx.grid(row=0, column=5, sticky=W)

        # Row 2: Errors
        ttk.Label(stats_grid, text="Errors:",
                 font=("Consolas", 10, "bold")).grid(row=1, column=0, sticky=W, padx=(0, 5), pady=(5, 0))
        self.stat_errors = ttk.Label(stats_grid, text="--",
                                    font=("Consolas", 10))
        self.stat_errors.grid(row=1, column=1, sticky=W, pady=(5, 0))

        # Title from script
        ttk.Label(stats_grid, text="Script title:",
                 font=("Consolas", 10, "bold")).grid(row=1, column=2, sticky=W, padx=(0, 5), pady=(5, 0))
        self.stat_title = ttk.Label(stats_grid, text="--",
                                   font=("Consolas", 10))
        self.stat_title.grid(row=1, column=3, columnspan=3, sticky=W, pady=(5, 0))

        # --- Speakers List ---
        speakers_frame = ttk.LabelFrame(scrollable, text="Detected Speakers", padding=10)
        speakers_frame.pack(fill=X, pady=(0, 10))

        lb_frame = ttk.Frame(speakers_frame)
        lb_frame.pack(fill=X, pady=5)

        lb_scrollbar = ttk.Scrollbar(lb_frame, orient="vertical")
        self.speakers_listbox = tk.Listbox(lb_frame, height=5,
                                          bg=APP_THEME["colors"]["inputbg"],
                                          fg=APP_THEME["colors"]["inputfg"],
                                          selectbackground=APP_THEME["colors"]["selectbg"],
                                          selectforeground=APP_THEME["colors"]["selectfg"],
                                          font=("Consolas", 10),
                                          relief="flat", borderwidth=1,
                                          highlightbackground=APP_THEME["colors"]["border"],
                                          yscrollcommand=lb_scrollbar.set)
        lb_scrollbar.config(command=self.speakers_listbox.yview)
        self.speakers_listbox.pack(side=LEFT, fill=X, expand=True)
        lb_scrollbar.pack(side=RIGHT, fill=Y)

        # --- Log Panel ---
        log_frame = ttk.LabelFrame(scrollable, text="Parse Log", padding=10)
        log_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        self.parse_log = scrolledtext.ScrolledText(log_frame, height=12,
                                                    font=("Consolas", 9),
                                                    bg=APP_THEME["colors"]["inputbg"],
                                                    fg=APP_THEME["colors"]["inputfg"],
                                                    insertbackground=APP_THEME["colors"]["inputfg"],
                                                    relief="flat", borderwidth=1,
                                                    state='disabled',
                                                    wrap='word')
        self.parse_log.pack(fill=BOTH, expand=True)

        # Configure log text tags for color coding
        self.parse_log.tag_configure("error", foreground="#FF6B6B")
        self.parse_log.tag_configure("success", foreground="#69DB7C")
        self.parse_log.tag_configure("info", foreground="#74C0FC")
        self.parse_log.tag_configure("warning", foreground="#FFD43B")
        self.parse_log.tag_configure("header", foreground=APP_THEME["colors"]["accent"],
                                    font=("Consolas", 10, "bold"))

        # --- Continue Button ---
        nav_frame = ttk.Frame(scrollable)
        nav_frame.pack(fill=X, pady=(5, 10))

        self.btn_continue_to_tab2 = ttk.Button(nav_frame,
                                               text="Continue to Voice Settings  >>",
                                               command=self.on_continue_to_tab2,
                                               bootstyle=SUCCESS, width=30,
                                               state="disabled")
        self.btn_continue_to_tab2.pack(side=RIGHT)

        # Bind mousewheel to all child widgets so scrolling works anywhere on the tab
        bind_mousewheel(scrollable)

    def log_message(self, text, tag=None):
        """Append a message to the parse log."""
        self.parse_log.config(state='normal')
        if tag:
            self.parse_log.insert('end', text + '\n', tag)
        else:
            self.parse_log.insert('end', text + '\n')
        self.parse_log.see('end')
        self.parse_log.config(state='disabled')

    def clear_log(self):
        """Clear the parse log."""
        self.parse_log.config(state='normal')
        self.parse_log.delete('1.0', 'end')
        self.parse_log.config(state='disabled')

    def update_stats(self, result):
        """Update the stats display from a ParseResult."""
        self.stat_lines.config(text=str(result.total_dialogue_lines))
        self.stat_speakers.config(text=str(len(result.speakers)))
        self.stat_sfx.config(text=str(len(result.sound_effects)))
        self.stat_title.config(text=result.title if result.title else "(none)")

        error_count = len(result.errors)
        if error_count == 0:
            self.stat_errors.config(text="0", foreground="#69DB7C")
        else:
            self.stat_errors.config(text=str(error_count), foreground="#FF6B6B")

        # Update speakers list
        self.speakers_listbox.delete(0, 'end')
        for speaker in result.speakers:
            self.speakers_listbox.insert('end', f"  {speaker}")

    def reset_stats(self):
        """Reset stats to default."""
        self.stat_lines.config(text="--")
        self.stat_speakers.config(text="--")
        self.stat_sfx.config(text="--")
        self.stat_errors.config(text="--", foreground=APP_THEME["colors"]["fg"])
        self.stat_title.config(text="--")
        self.speakers_listbox.delete(0, 'end')
