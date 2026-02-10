# ui/panels/footer.py — IDE status bar with run path + horizontal timeline

import tkinter as tk
from .base_panel import BasePanel
from ui.animations import ExecutionTimeline

FOOTER_BG = "#040810"
SEPARATOR = "#0d3a5a"


class Footer(BasePanel):
    """Fixed-height status bar at the bottom of the IDE window."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=FOOTER_BG, height=32, **kw)
        self.pack_propagate(False)
        self._build()

    def _build(self):
        # Status line (left side)
        self.status_line = tk.Label(
            self,
            text="Run: waiting",
            fg=self.BLUE2,
            bg=FOOTER_BG,
            font=("Consolas", 10),
            anchor="w",
        )
        self.status_line.pack(side="left", padx=(12, 0), pady=4)

        # Vertical separator
        sep = tk.Frame(self, bg=SEPARATOR, width=1)
        sep.pack(side="left", fill="y", padx=(12, 12), pady=4)

        # Timeline labels (right side, horizontal)
        timeline_frame = tk.Frame(self, bg=FOOTER_BG)
        timeline_frame.pack(side="right", padx=(0, 12), pady=4)
        self.timeline = ExecutionTimeline(
            timeline_frame, ("Consolas", 10, "bold"), orient="horizontal"
        )
        # Override the label bg to match footer
        for lbl in self.timeline.labels:
            lbl.configure(bg=FOOTER_BG)
