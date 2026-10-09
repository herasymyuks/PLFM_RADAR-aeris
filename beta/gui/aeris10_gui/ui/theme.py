"""Dark 'mercury' theme lifted from GUI_V5.py:44-55 and configure_dark_theme (:911-990)."""
from tkinter import ttk

DARK_BG = "#2b2b2b"
DARK_FG = "#e0e0e0"
DARK_ACCENT = "#3c3f41"
DARK_HIGHLIGHT = "#4e5254"
DARK_BORDER = "#555555"
DARK_TEXT = "#cccccc"
PLOT_BG = "#1a1a1a"


def apply_dark_theme(root, style: ttk.Style) -> None:
    root.configure(bg=DARK_BG)
    style.theme_use("clam")
    style.configure(".", background=DARK_BG, foreground=DARK_FG, fieldbackground=DARK_ACCENT,
                    selectbackground=DARK_HIGHLIGHT, selectforeground=DARK_FG, bordercolor=DARK_BORDER)
    style.configure("TFrame", background=DARK_BG)
    style.configure("TLabel", background=DARK_BG, foreground=DARK_FG)
    style.configure("TButton", background=DARK_ACCENT, foreground=DARK_FG, borderwidth=1)
    style.map("TButton", background=[("active", DARK_HIGHLIGHT), ("disabled", DARK_BG)])
    style.configure("TEntry", fieldbackground=DARK_ACCENT, foreground=DARK_FG, insertcolor=DARK_FG)
    style.configure("TCombobox", fieldbackground=DARK_ACCENT, foreground=DARK_FG, background=DARK_ACCENT)
    style.configure("TCheckbutton", background=DARK_BG, foreground=DARK_FG)
    style.configure("TNotebook", background=DARK_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=DARK_ACCENT, foreground=DARK_FG, padding=[10, 4])
    style.map("TNotebook.Tab", background=[("selected", DARK_HIGHLIGHT)])
    style.configure("Treeview", background=DARK_ACCENT, foreground=DARK_FG, fieldbackground=DARK_ACCENT)
    style.configure("Treeview.Heading", background=DARK_HIGHLIGHT, foreground=DARK_FG)
    style.configure("TLabelframe", background=DARK_BG, foreground=DARK_FG, bordercolor=DARK_BORDER)
    style.configure("TLabelframe.Label", background=DARK_BG, foreground=DARK_FG)
