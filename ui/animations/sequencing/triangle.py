"""Ritual triangle submit button behavior."""

import math
import tkinter as tk


class RitualTriangleButton(tk.Canvas):
    def __init__(self, master, command=None, w=104, h=86, **kw):
        super().__init__(master, width=w, height=h, bg=kw.pop("bg", "#050b14"), highlightthickness=0, bd=0, **kw)
        self.w = w
        self.h = h
        self.command = command
        self.hover = False
        self.pressed = False
        self.running = False
        self.locked = False
        self.scan_phase = 0
        self.ripple_phase = 0
        self.rotate_phase = 0
        self.glow_phase = 0

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_down)
        self.bind("<ButtonRelease-1>", self._on_up)
        self._draw()

    def set_enabled(self, enabled: bool):
        self.configure(state="normal" if enabled else "disabled")
        self._draw()

    def set_run_state(self, running: bool, locked: bool):
        self.running = running
        self.locked = locked
        if locked:
            self.ripple_phase = 0
        self._draw()

    def _on_enter(self, _):
        if not self.locked:
            self.hover = True
            self._draw()

    def _on_leave(self, _):
        self.hover = False
        self.pressed = False
        self.scan_phase = 0
        self._draw()

    def _on_down(self, _):
        if not self.locked and str(self.cget("state")) != "disabled":
            self.pressed = True
            self.ripple_phase = 4
            self._draw()

    def _on_up(self, e):
        was_pressed = self.pressed
        self.pressed = False
        self._draw()
        if was_pressed and 0 <= e.x <= self.w and 0 <= e.y <= self.h and self.command:
            self.command()

    def tick(self, enabled: bool):
        if self.locked:
            self.glow_phase = 0
            self.scan_phase = 0
            self.rotate_phase = 0
        else:
            self.glow_phase = (self.glow_phase + 1) % 12 if enabled else 0
            if self.hover:
                self.scan_phase = (self.scan_phase + 1) % 16
            if self.running:
                self.rotate_phase = (self.rotate_phase + 1) % 24
            if self.ripple_phase > 0:
                self.ripple_phase -= 1
        self._draw()

    def _draw(self):
        self.delete("all")

        if str(self.cget("state")) == "disabled":
            edge_outer = "#604522"
            edge_inner = "#25526a"
            fill = "#0f5e76"
        else:
            edge_outer = "#00d5ff" if not self.locked else "#7fe8ff"
            edge_inner = "#4fe3ff"
            fill = "#0a6f90" if self.running else "#0b7ea0"

        left_x, right_x, top_y, bottom_y = 15, self.w - 15, 10, self.h - 10
        mid_x = self.w // 2

        glow = 1 if self.glow_phase in (2, 6, 10) and not self.locked else 0

        for i in range(6 + glow):
            self.create_polygon(
                left_x - i, top_y + i,
                right_x + i, top_y + i,
                mid_x, bottom_y + i,
                fill="",
                outline=edge_outer,
                width=2,
            )

        for i in range(4):
            self.create_polygon(
                left_x + 8 - i, top_y + 11 + i,
                right_x - 8 + i, top_y + 11 + i,
                mid_x, bottom_y - 7 + i,
                fill="",
                outline=edge_inner,
                width=2,
            )

        self.create_polygon(
            left_x + 11, top_y + 14,
            right_x - 11, top_y + 14,
            mid_x, bottom_y - 10,
            fill=fill,
            outline="#4fe3ff",
            width=2,
        )

        if self.hover and not self.locked:
            scan_y = top_y + 16 + self.scan_phase
            if scan_y < bottom_y - 12:
                self.create_polygon(
                    left_x + 18, scan_y,
                    right_x - 18, scan_y,
                    mid_x, scan_y + 6,
                    fill="#5ff1ff",
                    outline="",
                    stipple="gray50",
                )

        if self.running and not self.locked:
            angle = (self.rotate_phase / 24) * (2 * math.pi)
            radius = 16
            rx = mid_x + int(math.cos(angle) * radius)
            ry = top_y + 26 + int(math.sin(angle) * radius)
            self.create_oval(rx - 3, ry - 3, rx + 3, ry + 3, fill="#d6fbff", outline="")

        if self.ripple_phase > 0 and not self.locked:
            ripple = 2 + (4 - self.ripple_phase) * 3
            self.create_polygon(
                left_x - ripple, top_y - ripple,
                right_x + ripple, top_y - ripple,
                mid_x, bottom_y + ripple,
                fill="",
                outline="#7fe8ff",
                width=1,
            )
