"""UI animation hooks for ICE-CRAWLER."""

import itertools


def start_snowflake_spin(label, root, interval_ms: int = 120):
    """Spin a snowflake label using a small glyph cycle."""
    frames = itertools.cycle(["❄", "✳", "✴", "✲", "✱", "✺"])

    def tick():
        label.configure(text=next(frames))
        root.after(interval_ms, tick)

    tick()
