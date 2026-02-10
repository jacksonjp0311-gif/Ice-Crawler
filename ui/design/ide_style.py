# ui/design/ide_style.py — ttk.Style configuration for IDE chrome

from tkinter import ttk


# IDE chrome color constants
SASH_COLOR = "#0a1929"
TAB_BG = "#0b1a2e"
TAB_FG = "#6fb9c9"
TAB_ACTIVE_BG = "#071427"
TAB_ACTIVE_FG = "#4fe3ff"
SIDEBAR_BG = "#050b14"
FOOTER_BG = "#040810"
TERMINAL_BG = "#050b14"
NOTEBOOK_BG = "#050b14"


def apply_ide_style(root):
    """Configure ttk styles for the IDE-like notebook tabs and sashes."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # Notebook (terminal tabs)
    style.configure(
        "IDE.TNotebook",
        background=NOTEBOOK_BG,
        borderwidth=0,
        tabmargins=[0, 0, 0, 0],
    )
    style.configure(
        "IDE.TNotebook.Tab",
        background=TAB_BG,
        foreground=TAB_FG,
        padding=[12, 4],
        font=("Consolas", 10, "bold"),
        borderwidth=0,
    )
    style.map(
        "IDE.TNotebook.Tab",
        background=[("selected", TAB_ACTIVE_BG)],
        foreground=[("selected", TAB_ACTIVE_FG)],
    )

    # Remove dotted focus ring on tabs
    style.layout("IDE.TNotebook.Tab", [
        ("Notebook.tab", {
            "sticky": "nswe",
            "children": [
                ("Notebook.padding", {
                    "side": "top",
                    "sticky": "nswe",
                    "children": [
                        ("Notebook.label", {"side": "top", "sticky": ""})
                    ]
                })
            ]
        })
    ])

    return style
