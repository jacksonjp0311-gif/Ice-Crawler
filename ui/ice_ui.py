# ui/ice_ui.py
# ❄ ICE-CRAWLER UI v4.8 — LADDER TRUTH LOCK + GLITCHLESS SURFACE

import os, threading, queue, time, subprocess
import tkinter as tk
from tkinter import ttk, messagebox

from design.layout import apply_style, build_surface

PHASES = ["Frost","Glacier","Crystal","Residue"]

def run_orchestrator(repo_root, repo_url):

    orch = os.path.join(repo_root,"engine","orchestrator.py")

    state_dir = os.path.join(repo_root,"state","runs")
    os.makedirs(state_dir, exist_ok=True)

    run_tag   = time.strftime("run_%Y%m%d_%H%M%S")
    state_run = os.path.join(state_dir, run_tag)
    os.makedirs(state_run, exist_ok=True)

    cmd = ["python", orch, repo_url, state_run, "50", "120"]

    p = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    return p.returncode, state_run


def read_events(state_run):
    ev = os.path.join(state_run,"ui_events.jsonl")
    if not os.path.exists(ev):
        return ""
    try:
        return open(ev,"r",encoding="utf-8").read()
    except:
        return ""


class IceCrawlerUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("ICE-CRAWLER ❄")
        self.geometry("950x880")

        self.repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__),"..")
        )

        self.q = queue.Queue()
        self.state_run = None

        # Truth-lock phase completion state
        self.phase_truth = {p: False for p in PHASES}

        # Event cache (prevents flicker)
        self.last_events = ""

        style = ttk.Style()
        apply_style(style)
        build_surface(self, PHASES)

        # Animation pulse index
        self.pulse = 0

        self.after(120, self._animate)
        self.after(250, self._pump)


    # ─────────────────────────────────────────────
    # LADDER ANIMATION (ONLY UNFINISHED PHASES)
    # ─────────────────────────────────────────────
    def _animate(self):

        self.pulse = (self.pulse + 1) % 16
        glow = "⬤" if self.pulse < 8 else "◉"

        for phase in PHASES:
            if not self.phase_truth[phase]:
                self.phase_labels[phase].config(text=f"{glow} {phase}")

        self.after(120, self._animate)


    # ─────────────────────────────────────────────
    # TRUTH SETTER (✓ NEVER OVERRIDDEN)
    # ─────────────────────────────────────────────
    def _lock_phase(self, phase):

        self.phase_truth[phase] = True
        lbl = self.phase_labels[phase]

        lbl.config(
            text=f"✓ {phase}",
            foreground="#6fe7ff"
        )


    def open_artifact(self):
        if self.state_run:
            os.startfile(self.state_run)


    # ─────────────────────────────────────────────
    # SUBMIT
    # ─────────────────────────────────────────────
    def on_submit(self):

        repo_url = self.url_entry.get().strip()
        if not repo_url or repo_url.startswith("Enter URL"):
            messagebox.showerror("ICE-CRAWLER","Repo URL required.")
            return

        self.submit_btn.config(state="disabled")
        self.progress["value"] = 10

        def work():
            rc, state_run = run_orchestrator(self.repo_root, repo_url)
            self.q.put(state_run)

        threading.Thread(target=work, daemon=True).start()


    # ─────────────────────────────────────────────
    # PUMP LOOP (NO FLICKER)
    # ─────────────────────────────────────────────
    def _pump(self):

        try:
            while True:
                self.state_run = self.q.get_nowait()
        except queue.Empty:
            pass

        if self.state_run:

            events = read_events(self.state_run)

            # Only update UI if events changed
            if events != self.last_events:

                self.last_events = events

                if "FROST_VERIFIED" in events:
                    self._lock_phase("Frost")

                if "GLACIER_VERIFIED" in events:
                    self._lock_phase("Glacier")

                if "CRYSTAL_VERIFIED" in events:
                    self._lock_phase("Crystal")

                if "RESIDUE_LOCK" in events:
                    self._lock_phase("Residue")

                # Progress truth
                self.progress["value"] = 100 if "CRYSTAL_VERIFIED" in events else 70

                # Artifact path
                proof = os.path.join(self.state_run,"ai_handoff_path.txt")
                if os.path.exists(proof):
                    path = open(proof,"r",encoding="utf-8").read().strip()
                    self.output_box.delete("1.0","end")
                    self.output_box.insert("end", path)

                # Fossil viewer tail
                self.event_view.delete("1.0","end")
                self.event_view.insert("end", events[-1400:])

                self.submit_btn.config(state="normal")

        self.after(250, self._pump)


if __name__=="__main__":
    IceCrawlerUI().mainloop()
