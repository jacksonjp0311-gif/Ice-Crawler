"""Snowflake icon handling for ICE-CRAWLER."""

import math
import tkinter as tk


class SnowflakeAnimator:
    def __init__(self, canvas: tk.Canvas, glow_ids, root: tk.Tk, interval_ms: int = 140):
        self.canvas = canvas
        self.glow_ids = glow_ids
        self.root = root
        self.interval_ms = interval_ms
        self.phase = 0.0

    def tick(self):
        self.phase += 0.08
        pulse = (math.sin(self.phase) + 1) / 2
        base = 18
        extra = int(6 * pulse)
        for idx, glow_id in enumerate(self.glow_ids):
            radius = base + extra + idx * 6
            cx, cy = 24, 24
            self.canvas.coords(glow_id, cx - radius, cy - radius, cx + radius, cy + radius)
            intensity = 0.22 + 0.18 * pulse
            color = "#6fdcff" if idx == 0 else "#2fb7ff"
            self.canvas.itemconfigure(glow_id, fill=color, stipple="gray50" if intensity < 0.3 else "gray25")
        self.root.after(self.interval_ms, self.tick)


def attach_snowflake(parent: tk.Widget, root: tk.Tk, image_path: str | None = None) -> tk.Canvas:
    canvas = tk.Canvas(parent, width=48, height=48, bg=parent.cget("bg"), highlightthickness=0, bd=0)
    glow_outer = canvas.create_oval(6, 6, 42, 42, fill="#2fb7ff", outline="", stipple="gray50")
    glow_inner = canvas.create_oval(10, 10, 38, 38, fill="#6fdcff", outline="", stipple="gray25")
    _draw_snowflake(canvas, 24, 24)
    animator = SnowflakeAnimator(canvas, [glow_outer, glow_inner], root)
    canvas.animator = animator
    animator.tick()
    return canvas


def _draw_snowflake(canvas: tk.Canvas, cx: int, cy: int) -> None:
    color = "#cfefff"
    for dx, dy in ((-12, 0), (12, 0), (0, -12), (0, 12), (-9, -9), (9, 9), (-9, 9), (9, -9)):
        canvas.create_line(cx, cy, cx + dx, cy + dy, fill=color, width=2)
    for dx, dy in ((-6, -2), (-6, 2), (6, -2), (6, 2)):
        canvas.create_line(cx + dx, cy + dy, cx + dx * 1.5, cy + dy * 1.5, fill=color, width=2)
    canvas.create_oval(cx - 2, cy - 2, cx + 2, cy + 2, fill=color, outline=color)
