"""Execution timeline panel."""


class ExecutionTimeline:
    def __init__(self, container, font):
        self.container = container
        self.font = font
        self.labels = []
        for _ in range(4):
            lbl = self._make_label("")
            lbl.pack(anchor="w")
            self.labels.append(lbl)
        self.reset()

    def _make_label(self, text):
        import tkinter as tk

        return tk.Label(self.container, text=text, fg="#4fe3ff", bg="#050b14", font=self.font)

    def reset(self):
        for lbl in self.labels:
            lbl.configure(text="")
        self.step = 0

    def update(self, events: str):
        ordered = ["FROST_VERIFIED", "GLACIER_VERIFIED", "CRYSTAL_VERIFIED", "RESIDUE_LOCK"]
        if "RESIDUE_EMPTY_LOCK" in events:
            ordered[-1] = "RESIDUE_EMPTY_LOCK"

        for idx, key in enumerate(ordered):
            if idx < len(self.labels):
                if key in events and self.labels[idx].cget("text") == "":
                    if all(self.labels[j].cget("text") for j in range(idx)):
                        text = self._label_for_key(key)
                        self.labels[idx].configure(text=text)

    def _label_for_key(self, key: str) -> str:
        mapping = {
            "FROST_VERIFIED": "[ Frost captured ]",
            "GLACIER_VERIFIED": "[ Glacier reduced ]",
            "CRYSTAL_VERIFIED": "[ Crystal locked ]",
            "RESIDUE_LOCK": "[ Residue emitted ]",
            "RESIDUE_EMPTY_LOCK": "[ Residue emitted ]",
        }
        return mapping.get(key, "")
