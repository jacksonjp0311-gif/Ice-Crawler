# ui/ice_ui.py
# ❄ ICE-CRAWLER UI v4.2U — Event-Truth Control Surface
#
# IMMUTABLE UI LAW
#  • UI never runs git
#  • UI never touches engine substrate
#  • UI reads ONLY emitted fossils:
#      - state/runs/<latest>/ui_events.jsonl
#      - state/runs/<latest>/ai_handoff_path.txt
#      - state/runs/<latest>/ai_handoff/root_seal.txt
#  • UI phases update ONLY from ui_events.jsonl
#
# UI is observational only. Orchestrator is sole authority.

import os, threading, queue, time, subprocess
import tkinter as tk
from tkinter import ttk, messagebox

PHASES = ["Frost", "Glacier", "Crystal", "Residue"]

# ─────────────────────────────────────────────────────────────
# ORCHESTRATOR LAUNCH (UI NEVER RUNS GIT)
# ─────────────────────────────────────────────────────────────

def run_orchestrator(repo_root, repo_url):

    orch = os.path.join(repo_root, "engine", "orchestrator.py")

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


# ─────────────────────────────────────────────────────────────
# EVENT-TRUTH READER
# ─────────────────────────────────────────────────────────────

def read_events(state_run):
    ev = os.path.join(state_run, "ui_events.jsonl")
    if not os.path.exists(ev):
        return ""
    try:
        return open(ev,"r",encoding="utf-8").read()
    except:
        return ""


# ─────────────────────────────────────────────────────────────
# UI APP (OBSERVATIONAL SURFACE)
# ─────────────────────────────────────────────────────────────

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
        self.state_run = None

        self._build()
        self.after(200, self._pump)

        def _build(self):

        style = ttk.Style()
        style.theme_use("clam")

        # GLOBAL COLORS (PHOTO-LOCK)
        BG      = "#05080d"
        PANEL   = "#0b141c"
        CYAN    = "#6fe7ff"
        CYAN2   = "#3bbcd6"
        TEXT    = "#d8fbff"

        self.configure(bg=BG)

        style.configure("TFrame", background=BG)

        style.configure("TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 16)
        )

        style.configure("TButton",
            font=("Segoe UI", 18, "bold"),
            padding=14
        )

        # ─────────────────────────────
        # TOP URL PANEL
        # ─────────────────────────────
        top = ttk.Frame(self, padding=18)
        top.pack(fill="x")

        self.url_entry = ttk.Entry(
            top,
            font=("Segoe UI", 20)
        )
        self.url_entry.pack(fill="x", pady=(0, 16))
        self.url_entry.insert(0, "Enter URL or GitHub URL")

        self.submit_btn = ttk.Button(
            top,
            text="Submit to Ice-Crawler",
            command=self.on_submit
        )
        self.submit_btn.pack(fill="x")

        # ─────────────────────────────
        # CENTER BODY
        # ─────────────────────────────
        mid = ttk.Frame(self, padding=25)
        mid.pack(fill="both", expand=True)

        # LEFT LADDER
        ladder = ttk.Frame(mid)
        ladder.pack(side="left", padx=30)

        self.phase_labels = {}
        for phase in PHASES:
            lbl = ttk.Label(
                ladder,
                text=f"⬤ {phase}",
                font=("Segoe UI", 22)
            )
            lbl.pack(anchor="w", pady=18)
            self.phase_labels[phase] = lbl

        # CENTER LOGO BLOCK
        logo = ttk.Frame(mid)
        logo.pack(side="left", expand=True)

        ttk.Label(
            logo,
            text="ICE\nCRAWLER ❄",
            font=("Segoe UI", 54, "bold"),
            justify="center",
            foreground=CYAN
        ).pack(pady=50)

        # ─────────────────────────────
        # PROGRESS BAR
        # ─────────────────────────────
        style.configure("Ice.Horizontal.TProgressbar",
            troughcolor="#111820",
            background=CYAN2,
            thickness=26
        )

        self.progress = ttk.Progressbar(
            self,
            style="Ice.Horizontal.TProgressbar",
            mode="determinate",
            maximum=100
        )
        self.progress.pack(fill="x", padx=60, pady=20)

        # ─────────────────────────────
        # OUTPUT PANEL
        # ─────────────────────────────
        bottom = ttk.Frame(self, padding=22)
        bottom.pack(fill="x")

        ttk.Label(
            bottom,
            text="Copy paste this link to the artifact on your local device:",
            font=("Segoe UI", 18)
        ).pack(anchor="w", pady=(0, 12))

        self.output_box = tk.Text(
            bottom,
            height=2,
            font=("Consolas", 16),
            bg="#0d1117",
            fg=CYAN,
            relief="flat"
        )
        self.output_box.pack(fill="x")

    def _set_phase(self, phase, verified):
        lbl = self.phase_labels[phase]
        if verified:
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

        def work():
            rc, state_run = run_orchestrator(self.repo_root, repo_url)
            self.q.put(state_run)

        threading.Thread(target=work, daemon=True).start()

    def _pump(self):

        try:
            while True:
                self.state_run = self.q.get_nowait()

        except queue.Empty:
            pass

        if self.state_run:

            events = read_events(self.state_run)

            self._set_phase("Frost",   "FROST_VERIFIED"   in events)
            self._set_phase("Glacier", "GLACIER_VERIFIED" in events)
            self._set_phase("Crystal", "CRYSTAL_VERIFIED" in events)
            self._set_phase("Residue", "RESIDUE_LOCK"     in events)

            self.progress["value"] = 100 if "CRYSTAL_VERIFIED" in events else 50

            proof = os.path.join(self.state_run, "ai_handoff_path.txt")
            if os.path.exists(proof):
                path = open(proof,"r",encoding="utf-8").read().strip()
                self.output_box.delete("1.0","end")
                self.output_box.insert("end", path)

        self.after(200, self._pump)


if __name__=="__main__":
    IceCrawlerUI().mainloop()

