"""Handoff complete badge for ICE-CRAWLER."""

import math
import tkinter as tk


class HandoffCompleteBadge(tk.Frame):
    def __init__(self, master, command=None, **kw):
        super().__init__(master, bg=kw.pop("bg", "#050b14"), **kw)
        self.command = command
        self._build()

    def _build(self):
        self.icon = tk.Canvas(self, width=70, height=60, bg=self.cget("bg"), highlightthickness=0, bd=0)
        self.icon.pack(side="left")
        self._draw_triangle()

        self.label_frame = tk.Frame(self, bg=self.cget("bg"), highlightbackground="#ff9b1a", highlightthickness=2)
        self.label_frame.pack(side="left", padx=(6, 0))
        self.label = tk.Label(
            self.label_frame,
            text="handoff complete — click here",
            fg="#ff9b1a",
            bg=self.cget("bg"),
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
        )
        self.label.pack(padx=12, pady=6)
        self.label.bind("<Button-1>", self._on_click)
        self.icon.bind("<Button-1>", self._on_click)

    def _on_click(self, _event):
        if self.command:
            self.command()

    def _draw_triangle(self):
        self.icon.delete("all")
        w, h = 70, 60
        left_x, right_x, top_y, bottom_y = 10, w - 10, 6, h - 6
        mid_x = w // 2
        edge_outer = "#ff9b1a"
        edge_inner = "#ff6a00"
        fill = "#a85000"

        for i in range(5):
            self.icon.create_polygon(
                left_x - i,
                top_y + i,
                right_x + i,
                top_y + i,
                mid_x,
                bottom_y + i,
                fill="",
                outline=edge_outer,
                width=2,
            )

        for i in range(3):
            self.icon.create_polygon(
                left_x + 6 - i,
                top_y + 8 + i,
                right_x - 6 + i,
                top_y + 8 + i,
                mid_x,
                bottom_y - 6 + i,
                fill="",
                outline=edge_inner,
                width=2,
            )

        self.icon.create_polygon(
            left_x + 8,
            top_y + 10,
            right_x - 8,
            top_y + 10,
            mid_x,
            bottom_y - 8,
            fill=fill,
            outline="#ffd3a3",
            width=2,
        )
