# ui/ice_ui.py
# ❄ ICE-CRAWLER UI v1.0 — Frost → Glacier → Crystal Control Surface
# UI is observational only. Orchestrator is sole authority.
#
# IMMUTABLE UI LAW
#  • UI never runs git
#  • UI never touches repo substrate directly
#  • UI reads ONLY emitted fossils:
#      - ui_events.jsonl
#      - ai_handoff_path.txt
#      - manifest_compact.json
#      - root_seal.txt
#  • UI may anchor local folders (state/runs) for deterministic operation

import os, threading, queue, time, subprocess
import tkinter as tk
from tkinter import ttk, messagebox

PHASES = ["Frost", "Glacier", "Crystal"]

# ─────────────────────────────────────────────────────────────
# ORCHESTRATOR LAUNCH (UI NEVER RUNS GIT)
# ─────────────────────────────────────────────────────────────

def run_orchestrator(repo_root, repo_url, max_files, max_kb):

    engine = os.path.join(repo_root, "engine")
    orch   = os.path.join(engine, "orchestrator.py")

    # UI anchors only local fossil surface
    state_dir = os.path.join(repo_root, "state", "runs")
    os.makedirs(state_dir, exist_ok=True)

    run_tag   = time.strftime("run_%Y%m%d_%H%M%S")
    state_run = os.path.join(state_dir, run_tag)
    os.makedirs(state_run, exist_ok=True)

    tempw = os.path.join(
        os.environ.get("TEMP", "."),
        "icecrawl_ui_" + str(int(time.time()*1000))
    )

    cmd = [
        "python", orch,
        repo_url,
        state_run,
        str(max_files),
        str(max_kb),
        tempw
    ]

    p = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    return p.returncode, p.stdout, state_run


# ─────────────────────────────────────────────────────────────
# UI APP (MATCH SCREENSHOT)
# ─────────────────────────────────────────────────────────────

class IceCrawlerUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("ICE-CRAWLER ❄")
        self.geometry("880x620")
        self.configure(bg="#05080d")

        self.repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )

        # Allowed: anchor UI-local surfaces
        os.makedirs(os.path.join(self.repo_root, "state", "runs"), exist_ok=True)

        self.q = queue.Queue()
        self._build()
        self.after(150, self._pump)

    def _build(self):

        # URL ENTRY
        top = ttk.Frame(self, padding=14)
        top.pack(fill="x")

        self.url_entry = ttk.Entry(top, font=("Segoe UI", 14))
        self.url_entry.pack(fill="x", pady=(0, 10))
        self.url_entry.insert(0, "Enter URL or GitHub URL")

        self.submit_btn = ttk.Button(
            top,
            text="Submit to Ice-Crawler",
            command=self.on_submit
        )
        self.submit_btn.pack(fill="x")

        # BODY
        mid = ttk.Frame(self, padding=18)
        mid.pack(fill="both", expand=True)

        # PHASE LADDER
        ladder = ttk.Frame(mid)
        ladder.pack(side="left", padx=20)

        self.phase_labels = {}
        for phase in PHASES:
            lbl = ttk.Label(ladder, text=f"⬤ {phase}", font=("Segoe UI", 16))
            lbl.pack(anchor="w", pady=14)
            self.phase_labels[phase] = lbl

        # LOGO
        logo = ttk.Frame(mid)
        logo.pack(side="left", expand=True)

        ttk.Label(
            logo,
            text="ICE\nCRAWLER ❄",
            font=("Segoe UI", 38, "bold"),
            justify="center"
        ).pack(pady=40)

        # PROGRESS
        self.progress = ttk.Progressbar(self, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=40, pady=12)

        # OUTPUT
        bottom = ttk.Frame(self, padding=18)
        bottom.pack(fill="x")

        ttk.Label(
            bottom,
            text="Copy paste this link to the artifact on your local device:",
            font=("Segoe UI", 13)
        ).pack(anchor="w")

        self.output_box = tk.Text(bottom, height=2, font=("Consolas", 12))
        self.output_box.pack(fill="x", pady=8)

    def on_submit(self):

        repo_url = self.url_entry.get().strip()
        if not repo_url or repo_url.startswith("Enter URL"):
            messagebox.showerror("ICE-CRAWLER", "Repo URL required.")
            return

        self.submit_btn.config(state="disabled")
        self.progress["value"] = 5

        self._set_phase("Frost", "pending")

        def work():
            rc, out, state_run = run_orchestrator(
                self.repo_root,
                repo_url,
                max_files=50,
                max_kb=120
            )
            self.q.put((rc, out, state_run))

        threading.Thread(target=work, daemon=True).start()

    def _set_phase(self, phase, state):
        lbl = self.phase_labels[phase]
        if state == "pending":
            lbl.config(text=f"⬤ {phase} …")
        elif state == "verified":
            lbl.config(text=f"✓ {phase}")
        else:
            lbl.config(text=f"⬤ {phase}")

    def _pump(self):
        try:
            while True:
                rc, out, state_run = self.q.get_nowait()

                self._set_phase("Frost", "verified")
                self._set_phase("Glacier", "verified")
                self._set_phase("Crystal", "verified")
                self.progress["value"] = 100

                proof_file = os.path.join(state_run, "ai_handoff_path.txt")
                path = "(missing ai_handoff_path.txt)"
                if os.path.exists(proof_file):
                    path = open(proof_file,"r",encoding="utf-8").read().strip()

                self.output_box.delete("1.0", "end")
                self.output_box.insert("end", path)

                self.submit_btn.config(state="normal")

        except queue.Empty:
            pass

        self.after(150, self._pump)


if __name__ == "__main__":
    app = IceCrawlerUI()
    app.mainloop()
