# ui/panels/right_sidebar.py — CMD Stream, CMD Trace, Run Thread log boxes

import tkinter as tk
from .base_panel import BasePanel


class RightSidebar(BasePanel):
    """Three stacked read-only log panels."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._build()

    def _build(self):
        self.stream_text = self._make_log_box("CMD STREAM")
        self.cmd_text = self._make_log_box("CMD TRACE")
        self.thread_text = self._make_log_box("RUN THREAD")

    def _make_log_box(self, title):
        panel = tk.Frame(
            self, bg=self.BG, highlightbackground=self.BLUE2, highlightthickness=1
        )
        panel.pack(fill="both", expand=True, padx=4, pady=(4, 0))
        panel.pack_propagate(False)

        tk.Label(
            panel,
            text=title,
            fg=self.BLUE2,
            bg=self.BG,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=8, pady=(6, 2))

        text = tk.Text(
            panel,
            bg=self.TEXT_BG,
            fg=self.BLUE2,
            insertbackground=self.BLUE2,
            relief="flat",
            font=("Consolas", 9),
            wrap="word",
        )
        text.pack(fill="both", expand=True, padx=8, pady=(0, 6))
        text.configure(state="disabled")
        return text
