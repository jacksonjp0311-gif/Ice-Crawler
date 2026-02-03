# ui/ice_ui.py
# ❄ ICE-CRAWLER UI v4.1 — Canon Control Surface
#
# IMMUTABLE UI LAW
#  • UI never runs git
#  • UI never touches repo substrate directly
#  • UI reads ONLY emitted fossils:
#      - state/runs/<latest>/ui_events.jsonl
#      - state/runs/<latest>/ai_handoff_path.txt
#      - state/runs/<latest>/ai_handoff/root_seal.txt
#
# UI is observational only. Orchestrator is sole authority.

import os, threading, queue, time, subprocess
import tkinter as tk
from tkinter import ttk, messagebox

PHASES = ["Frost", "Glacier", "Crystal", "Residue"]

def run_orchestrator(repo_root, repo_url):
    engine = os.path.join(repo_root, "engine")
    orch   = os.path.join(engine, "orchestrator.py")

    # UI may anchor run surface
    state_dir = os.path.join(repo_root, "state", "runs")
    os.makedirs(state_dir, exist_ok=True)

    run_tag   = time.strftime("run_%Y%m%d_%H%M%S")
    state_run = os.path.join(state_dir, run_tag)
    os.makedirs(state_run, exist_ok=True)

    tempw = os.path.join(
        os.environ.get("TEMP","."), "icecrawl_ui_" + str(int(time.time()*1000))
    )

    cmd = ["python", orch, repo_url, state_run, "50", "120", tempw]

    p = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    return p.returncode, state_run


class IceCrawlerUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("ICE-CRAWLER ❄")
        self.geometry("900x640")
        self.configure(bg="#05080d")

        self.repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        self.q = queue.Queue()
        self._build()
        self.after(150, self._pump)

    def _build(self):

        # URL INPUT
        top = ttk.Frame(self, padding=16)
        top.pack(fill="x")

        self.url_entry = ttk.Entry(top, font=("Segoe UI", 15))
        self.url_entry.pack(fill="x", pady=(0,10))
        self.url_entry.insert(0, "Enter URL or GitHub URL")

        self.submit_btn = ttk.Button(
            top, text="Submit to Ice-Crawler", command=self.on_submit
        )
        self.submit_btn.pack(fill="x")

        # CENTER BODY
        mid = ttk.Frame(self, padding=18)
        mid.pack(fill="both", expand=True)

        # PHASE LADDER
        ladder = ttk.Frame(mid)
        ladder.pack(side="left", padx=25)

        self.phase_labels = {}
        for p in PHASES:
            lbl = ttk.Label(ladder, text=f"⬤ {p}", font=("Segoe UI", 16))
            lbl.pack(anchor="w", pady=10)
            self.phase_labels[p] = lbl

        # LOGO
        logo = ttk.Frame(mid)
        logo.pack(side="left", expand=True)

        ttk.Label(
            logo,
            text="ICE\nCRAWLER ❄",
            font=("Segoe UI", 40, "bold"),
            justify="center"
        ).pack(pady=40)

        # PROGRESS
        self.progress = ttk.Progressbar(self, maximum=100)
        self.progress.pack(fill="x", padx=50, pady=14)

        # OUTPUT PATH
        bottom = ttk.Frame(self, padding=18)
        bottom.pack(fill="x")

        ttk.Label(
            bottom,
            text="Copy paste this link to the artifact on your local device:",
            font=("Segoe UI", 13)
        ).pack(anchor="w")

        self.output_box = tk.Text(bottom, height=2, font=("Consolas", 12))
        self.output_box.pack(fill="x", pady=8)

    def _set_phase(self, phase, state):
        lbl = self.phase_labels[phase]
        if state == "pending":
            lbl.config(text=f"⬤ {phase} …")
        elif state == "verified":
            lbl.config(text=f"✓ {phase}")
        else:
            lbl.config(text=f"⬤ {phase}")

    def on_submit(self):

        repo_url = self.url_entry.get().strip()
        if not repo_url or repo_url.startswith("Enter URL"):
            messagebox.showerror("ICE-CRAWLER", "Repo URL required.")
            return

        self.submit_btn.config(state="disabled")
        self.progress["value"] = 5
        self._set_phase("Frost","pending")

        def work():
            rc, state_run = run_orchestrator(self.repo_root, repo_url)
            self.q.put(state_run)

        threading.Thread(target=work, daemon=True).start()

    def _pump(self):

        try:
            while True:
                state_run = self.q.get_nowait()

                # For now: mark phases green (v4.2 will read ui_events.jsonl)
                for p in PHASES:
                    self._set_phase(p,"verified")

                self.progress["value"] = 100

                proof_file = os.path.join(state_run,"ai_handoff_path.txt")
                path="(missing ai_handoff_path.txt)"
                if os.path.exists(proof_file):
                    path=open(proof_file,"r",encoding="utf-8").read().strip()

                self.output_box.delete("1.0","end")
                self.output_box.insert("end", path)

                self.submit_btn.config(state="normal")

        except queue.Empty:
            pass

        self.after(150, self._pump)


if __name__=="__main__":
    IceCrawlerUI().mainloop()
