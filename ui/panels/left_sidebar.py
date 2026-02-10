# ui/panels/left_sidebar.py — Phase ladder + agent status + handoff badge

import tkinter as tk
from .base_panel import BasePanel
from ui.animations import HandoffCompleteBadge

PHASES = ["Frost", "Glacier", "Crystal", "Residue"]


class LeftSidebar(BasePanel):
    """Phase ladder, agent status row, and handoff badge."""

    def __init__(self, master, handoff_command=None, **kw):
        super().__init__(master, **kw)
        self.handoff_command = handoff_command
        self.phase_dots = {}
        self.phase_labels = {}
        self.phase_checks = {}
        self.phase_reveals = {}
        self._build()

    def _build(self):
        # Section header
        tk.Label(
            self,
            text="PHASES",
            fg=self.DIM,
            bg=self.BG,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        # Phase ladder rows
        for p in PHASES:
            row = tk.Frame(self, bg=self.BG)
            row.pack(anchor="w", padx=12, pady=2, fill="x")

            dot = tk.Label(
                row, text="\u25cb", fg=self.BLUE2, bg=self.BG,
                font=("Segoe UI", 18, "bold"),
            )
            dot.pack(side="left")

            lbl = tk.Label(
                row, text=p, fg=self.BLUE2, bg=self.BG,
                font=("Segoe UI", 14, "bold"),
            )
            lbl.pack(side="left", padx=(6, 6))

            check = tk.Label(
                row, text="", fg=self.BLUE2, bg=self.BG,
                font=("Segoe UI", 12, "bold"),
            )
            check.pack(side="left", padx=(0, 4))

            reveal = tk.Label(
                row, text="", fg=self.ORANGE, bg=self.BG,
                font=("Segoe UI", 10, "italic"),
            )
            reveal.pack(side="left")

            self.phase_dots[p] = dot
            self.phase_labels[p] = lbl
            self.phase_checks[p] = check
            self.phase_reveals[p] = reveal

        # Separator
        tk.Frame(self, bg="#0d3a5a", height=1).pack(fill="x", padx=12, pady=(10, 8))

        # Agent status row
        self.agent_status_row = tk.Frame(self, bg=self.BG)
        self.agent_status_row.pack(anchor="w", padx=12, pady=(2, 4))
        self.agent_status_row.pack_forget()

        self.agent_frame = tk.Frame(
            self.agent_status_row, bg=self.BG,
            highlightbackground=self.BLUE2, highlightthickness=2,
        )
        self.agent_label = tk.Label(
            self.agent_frame, text="AGENTS", fg=self.BLUE2, bg=self.BG,
            font=("Segoe UI", 10, "bold"),
        )
        self.agent_label.pack(padx=8, pady=4)
        self.agent_frame.pack(side="left")

        self.agent_state_frame = tk.Frame(
            self.agent_status_row, bg=self.BG,
            highlightbackground=self.BLUE2, highlightthickness=2,
        )
        self.agent_state_label = tk.Label(
            self.agent_state_frame, text="AGENTS: NOT RUN", fg=self.BLUE2, bg=self.BG,
            font=("Segoe UI", 10, "bold"),
        )
        self.agent_state_label.pack(padx=8, pady=4)
        self.agent_state_frame.pack(side="left", padx=(8, 0))

        # Handoff badge
        self.handoff_badge = HandoffCompleteBadge(self, command=self.handoff_command)
        self.handoff_badge.pack(anchor="w", padx=12, pady=(4, 8))
        self.handoff_badge.pack_forget()
