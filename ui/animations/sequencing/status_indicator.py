"""Status indicator control."""


class StatusIndicator:
    def __init__(self, label):
        self.label = label
        self.state = "IDLE"
        self.pulse = 0

    def set_status(self, status: str, color: str):
        if self.state != status:
            self.state = status
            self.label.configure(text=f"STATUS: {status}", fg=color)

    def tick(self, running: bool):
        if self.state == "CRAWLING" and running:
            self.pulse = (self.pulse + 1) % 6
            color = "#2fb7ff" if self.pulse in (1, 2, 3) else "#4fe3ff"
            self.label.configure(fg=color)
        else:
            self.pulse = 0

    def update(self, events: str, running: bool):
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self.set_status("RESIDUE SEALED", "#ff9b1a")
        elif "CRYSTAL_VERIFIED" in events:
            self.set_status("CRYSTAL LOCKED", "#ffffff")
        elif running:
            self.set_status("CRAWLING", "#4fe3ff")
        else:
            self.set_status("IDLE", "#6fdcff")
