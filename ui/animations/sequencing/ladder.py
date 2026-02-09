"""Stage ladder animation control."""

import math


class StageLadderAnimator:
    def __init__(self, root, phases, dots, labels, reveals, checks):
        self.root = root
        self.phases = phases
        self.dots = dots
        self.labels = labels
        self.reveals = reveals
        self.checks = checks
        self.phase_states = {p: "idle" for p in phases}
        self.phase_flash = {p: 0 for p in phases}
        self.phase_pulse = 0.0

    def reset(self):
        self.phase_states = {p: "idle" for p in self.phases}
        self.phase_flash = {p: 0 for p in self.phases}
        self.phase_pulse = 0.0
        for p in self.phases:
            self.dots[p].configure(text="○", fg="#4fe3ff")
            self.labels[p].configure(fg="#4fe3ff")
            self.reveals[p].configure(text="", fg="#4fe3ff")
            self.checks[p].configure(text="", fg="#4fe3ff")

    def update_from_events(self, events: str):
        def set_state(phase, state):
            if self.phase_states.get(phase) != state:
                self.phase_states[phase] = state
                if phase == "Crystal" and state in {"active", "locked"}:
                    self.phase_flash[phase] = 6

        if ("FROST_VERIFIED" in events) or ("UI_EVENT:FROST_PENDING_TO_VERIFIED" in events):
            set_state("Frost", "locked")
        elif ("FROST_PENDING" in events) or ("UI_EVENT:FROST_PENDING" in events):
            set_state("Frost", "active")
        else:
            set_state("Frost", "idle")

        if ("GLACIER_VERIFIED" in events) or ("UI_EVENT:GLACIER_VERIFIED" in events):
            set_state("Glacier", "locked")
        elif ("GLACIER_PENDING" in events) or ("UI_EVENT:GLACIER_PENDING" in events):
            set_state("Glacier", "active")
        else:
            set_state("Glacier", "idle")

        if ("CRYSTAL_VERIFIED" in events) or ("UI_EVENT:CRYSTAL_VERIFIED" in events):
            set_state("Crystal", "locked")
        elif ("CRYSTAL_PENDING" in events) or ("UI_EVENT:CRYSTAL_PENDING" in events):
            set_state("Crystal", "active")
        else:
            set_state("Crystal", "idle")

        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events) or ("UI_EVENT:RESIDUE_EMPTY_LOCK" in events):
            set_state("Residue", "locked")
        elif ("RESIDUE_PENDING" in events) or ("UI_EVENT:RESIDUE_PENDING" in events):
            set_state("Residue", "active")
        else:
            set_state("Residue", "idle")

    def tick(self):
        self.phase_pulse += 0.2
        pulse = (math.sin(self.phase_pulse) + 1) / 2

        for phase in self.phases:
            state = self.phase_states.get(phase)
            dot = self.dots[phase]
            label = self.labels[phase]
            reveal = self.reveals[phase]
            check = self.checks[phase]

            if state == "locked":
                dot.configure(text="●", fg="#c8fff1")
                label.configure(fg="#c8fff1")
                check.configure(text="✓", fg="#c8fff1")
                reveal.configure(fg="#ff9b1a")
            elif state == "active":
                if phase == "Frost":
                    color = "#2b6c8d" if pulse < 0.5 else "#4fb6d7"
                elif phase == "Glacier":
                    color = "#3fc2ff" if pulse < 0.5 else "#7fe8ff"
                elif phase == "Crystal":
                    color = "#e6f7ff" if pulse < 0.5 else "#ffffff"
                else:
                    color = "#ffb347" if pulse < 0.5 else "#ffd09a"
                dot.configure(text="◉", fg=color)
                label.configure(fg=color)
                check.configure(text="", fg=color)
                reveal.configure(fg="#ff9b1a")
            else:
                dot.configure(text="○", fg="#4fe3ff")
                label.configure(fg="#4fe3ff")
                check.configure(text="", fg="#4fe3ff")
                reveal.configure(fg="#4fe3ff")

            if phase == "Crystal" and self.phase_flash[phase] > 0:
                flash_color = "#ffffff" if self.phase_flash[phase] % 2 == 0 else "#cfefff"
                label.configure(fg=flash_color)
                dot.configure(fg=flash_color)
                self.phase_flash[phase] -= 1

        self.root.after(160, self.tick)
