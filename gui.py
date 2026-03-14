"""
Main GUI module for Script to Voice Generator.
Sets up ttkbootstrap window with 3-tab notebook layout.
"""

import sys
import webbrowser
from pathlib import Path
import ttkbootstrap as ttk

from config import APP_TITLE, APP_GEOMETRY, ICON_FILENAME
from config_manager import ConfigManager
from character_profiles import CharacterProfilesManager
from audio_generator import AudioGenerator
from gui_theme import apply_app_theme
from gui_tab1 import Tab1Builder
from gui_tab2 import Tab2Builder
from gui_tab2_state import Tab2StateMixin
from gui_tab3 import Tab3Builder
from gui_tab4 import Tab4Builder
from gui_handlers import GUIHandlers
from gui_generation import GenerationMixin


class ScriptToVoiceGUI(Tab1Builder, Tab2Builder, Tab2StateMixin, Tab3Builder, Tab4Builder, GUIHandlers, GenerationMixin):
    """Main GUI application - 4-tab layout via multiple inheritance mixins"""

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        self.root.state('zoomed')  # Start maximized

        self._setup_window_theme()

        # Initialize backend components
        self.config_manager = ConfigManager()
        self.char_profiles = CharacterProfilesManager()
        creds = self.config_manager.get_ui("google_credentials_path")
        self.audio_gen = AudioGenerator(credentials_path=creds or None)

        # State
        self._current_script_path = None
        self._last_parse_result = None

        # Build UI
        self._build_ui()
        self._prefill_persisted_folders()

        # Refresh Tab 3 summary whenever the user switches to it
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Set window icon after full UI init (deferred so ttkbootstrap theme doesn't override it)
        self.root.after(0, self._setup_icon)

        # Start loading voices in background
        self.root.after(100, self._load_voices_async)

        # Show welcome popup on startup if enabled
        self.root.after(200, self._show_welcome_if_enabled)

    def _setup_icon(self):
        """Setup application icon"""
        try:
            if getattr(sys, 'frozen', False):
                app_path = Path(sys.executable).parent
            else:
                app_path = Path(__file__).parent

            icon_path = app_path / ICON_FILENAME
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Could not load icon: {e}")

    def _setup_window_theme(self):
        """Setup dark title bar on Windows"""
        try:
            import ctypes
            HWND = ctypes.windll.user32.GetParent(self.root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                HWND, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(ctypes.c_int(1)), ctypes.sizeof(ctypes.c_int)
            )
        except Exception:
            pass

    def _on_tab_changed(self, event):
        """Fire side-effects when the user switches tabs via the tab bar."""
        selected = self.notebook.index(self.notebook.select())
        if selected == 2:  # Tab 3 — Generate
            self._refresh_summary()
        elif selected == 3:  # Tab 4 — Settings
            self._refresh_tab4_usage()

    def _prefill_persisted_folders(self):
        """Prefill output folder and SFX folder from last-used config values."""
        import os
        saved_output = self.config_manager.get_ui("last_output_folder")
        if saved_output and not self._gen_output_folder_var.get():
            self._gen_output_folder_var.set(saved_output)

        saved_sfx = self.config_manager.get_ui("last_sfx_folder")
        if saved_sfx and os.path.isdir(saved_sfx) and not self._sfx_folder_var.get():
            self._sfx_folder_var.set(saved_sfx)

    def _build_ui(self):
        """Build the 4-tab notebook interface"""
        # Status bar at the bottom (packed first so it stays pinned to bottom)
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom", padx=5, pady=(0, 5))

        self.status_label = ttk.Label(status_frame, text="Ready",
                                     font=("Consolas", 9),
                                     foreground="#74C0FC")
        self.status_label.pack(side="left")

        self.retry_voices_btn = ttk.Button(status_frame, text="Retry",
                                           command=self._on_retry_voices,
                                           bootstyle="link",
                                           cursor="hand2")
        # Hidden until a voice-load error occurs
        self.retry_voices_btn.pack_forget()

        # Author footer — right side of status bar, same elevation
        author_link = ttk.Label(status_frame,
                                text="Made by Reactorcore",
                                font=("Consolas", 9, "underline"),
                                foreground="#60CDFF",
                                cursor="hand2")
        author_link.pack(side="right", padx=(0, 5))
        author_link.bind("<Button-1>",
                         lambda e: webbrowser.open("https://linktr.ee/reactorcore"))

        # Notebook container — Help button floats at top-right of notebook tab bar
        notebook_frame = ttk.Frame(self.root)
        notebook_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(fill="both", expand=True)

        # Help button placed at top-right of the notebook (floats over tab bar)
        self._btn_help = ttk.Button(notebook_frame, text="Help",
                                    command=self.on_help,
                                    bootstyle="info-outline", width=8)
        self._btn_help.place(relx=1.0, rely=0.0, anchor="ne", x=-2, y=2)

        # Tab 1: Script Loading
        tab1_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab1_frame, text="  1. Load Script  ")
        self.build_tab1(tab1_frame)

        # Tab 2: Voice Settings
        tab2_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab2_frame, text="  2. Voice Settings  ")
        self.build_tab2(tab2_frame)

        # Tab 3: Generation
        tab3_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab3_frame, text="  3. Generate  ")
        self.build_tab3(tab3_frame)

        # Tab 4: Settings
        tab4_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab4_frame, text="  4. Settings  ")
        self.build_tab4(tab4_frame)


def main():
    """Main entry point"""
    root = ttk.Window(themename="cyborg")
    apply_app_theme(root)
    app = ScriptToVoiceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
