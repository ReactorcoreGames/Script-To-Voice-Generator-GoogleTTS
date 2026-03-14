"""
Theme and styling utilities for Script to Voice Generator GUI
"""

from ttkbootstrap import Style
from config import APP_THEME


def apply_app_theme(root):
    """Apply custom dark theme to the application"""
    style = Style()
    colors = APP_THEME["colors"]

    root.configure(bg=colors["bg"])

    # Base style
    style.configure(".",
                   background=colors["bg"],
                   foreground=colors["fg"],
                   bordercolor=colors["border"],
                   darkcolor=colors["bg"],
                   lightcolor=colors["selectbg"],
                   troughcolor=colors["inputbg"],
                   selectbackground=colors["selectbg"],
                   selectforeground=colors["selectfg"],
                   fieldbackground=colors["inputbg"],
                   font=("Consolas", 10),
                   borderwidth=1)

    # Frame styles
    style.configure("TFrame", background=colors["bg"])
    style.configure("TLabelframe", background=colors["bg"],
                   bordercolor=colors["border"],
                   foreground=colors["fg"])
    style.configure("TLabelframe.Label", background=colors["bg"],
                   foreground=colors["accent"],
                   font=("Consolas", 11, "bold"))

    # Label styles
    style.configure("TLabel", background=colors["bg"],
                   foreground=colors["fg"])

    # Notebook (tab) styles
    style.configure("TNotebook", background=colors["bg"],
                   bordercolor=colors["border"])
    style.configure("TNotebook.Tab",
                   background=colors["inputbg"],
                   foreground=colors["fg"],
                   padding=[12, 6],
                   font=("Consolas", 10, "bold"))
    style.map("TNotebook.Tab",
             background=[("selected", colors["primary"]),
                        ("active", colors["active"])],
             foreground=[("selected", colors["selectfg"])])

    # Entry and Combobox
    style.configure("TEntry", fieldbackground=colors["inputbg"],
                   foreground=colors["inputfg"],
                   bordercolor=colors["border"],
                   insertcolor=colors["inputfg"])
    style.configure("TCombobox", fieldbackground=colors["inputbg"],
                   background=colors["inputbg"],
                   foreground=colors["inputfg"],
                   bordercolor=colors["border"],
                   arrowcolor=colors["fg"])
    style.map("TCombobox",
             fieldbackground=[("readonly", colors["inputbg"])])

    # Checkbutton and Radiobutton
    style.configure("TCheckbutton", background=colors["bg"],
                   foreground=colors["fg"])
    style.configure("TRadiobutton", background=colors["bg"],
                   foreground=colors["fg"])

    # Scale (slider)
    style.configure("TScale", background=colors["bg"],
                   troughcolor=colors["inputbg"],
                   bordercolor=colors["border"],
                   darkcolor=colors["primary"],
                   lightcolor=colors["primary"])

    # Button styles
    style.configure("info.TButton",
                   background=colors["info"],
                   foreground=colors["selectfg"],
                   bordercolor=colors["border"],
                   focuscolor=colors["active"])
    style.map("info.TButton",
             background=[("active", colors["active"])])

    style.configure("warning.TButton",
                   background=colors["warning"],
                   foreground=colors["selectfg"],
                   bordercolor=colors["border"])
    style.map("warning.TButton",
             background=[("active", colors["primary"])])

    style.configure("success.TButton",
                   background=colors["success"],
                   foreground=colors["selectfg"],
                   bordercolor="#00305A")
    style.map("success.TButton",
             background=[("active", "#1A8FE3")])

    style.configure("primary.TButton",
                   background=colors["primary"],
                   foreground=colors["selectfg"],
                   bordercolor=colors["border"])
    style.map("primary.TButton",
             background=[("active", colors["active"])])

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                   background=colors["inputbg"],
                   troughcolor=colors["bg"],
                   bordercolor=colors["border"],
                   arrowcolor=colors["fg"])

    # Separator
    style.configure("TSeparator", background=colors["border"])

    # Progressbar
    style.configure("TProgressbar",
                   background=colors["primary"],
                   troughcolor=colors["inputbg"],
                   bordercolor=colors["border"])
