# ui/ice_ui.py
# ❄ ICE-CRAWLER UI v4.3D — Event-Truth + Photo-Lock Control Surface
#
# IMMUTABLE UI LAW
#  • UI never runs git
#  • UI never touches engine substrate
#  • UI reads ONLY fossils:
#      - ui/latest_run_path.txt                     (points to state/runs/<run>)
#      - <run>/ui_events.jsonl                      (truth ladder source)
#      - <run>/ai_handoff_path.txt                  (artifact pointer)
#      - <run>/root_seal.txt                        (optional seal text)
#  • UI phases update ONLY from ui_events.jsonl
#
# NOTE
#  • This UI may launch the orchestrator, but it does NOT perform git actions.
#  • Orchestrator outputs are written into state/runs/<run>/ by engine layer.

import os, sys, threading, queue, time, subprocess, traceback
import tkinter as tk
from tkinter import ttk, messagebox

PHASES = ["Frost", "Glacier", "Crystal", "Residue"]

PLACEHOLDER = "Paste a GitHub URL (recommended) or repo URL..."
EVENT_FILE  = "ui_events.jsonl"

# ─────────────────────────────────────────────────────────────
# PATHS (dev + frozen-safe)
# ─────────────────────────────────────────────────────────────
def is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def repo_root():
    # Frozen: folder containing the exe; Dev: repo root from ui/
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def ui_dir():
    return os.path.join(repo_root(), "ui")

def latest_run_path_file():
    return os.path.join(ui_dir(), "latest_run_path.txt")

def read_latest_run_path():
    p = latest_run_path_file()
    if not os.path.exists(p):
        return None
    try:
        s = open(p, "r", encoding="utf-8").read().strip()
        return s if s else None
    except:
        return None

def write_latest_run_path(run_path: str):
    try:
        open(latest_run_path_file(), "w", encoding="utf-8").write(run_path or "")
    except:
        pass

def read_text(path: str) -> str:
    if not path or (not os.path.exists(path)):
        return ""
    try:
        return open(path, "r", encoding="utf-8").read()
    except:
        return ""

def read_events(run_path: str) -> str:
    return read_text(os.path.join(run_path, EVENT_FILE)) if run_path else ""

def ensure_runs_dir():
    os.makedirs(os.path.join(repo_root(), "state", "runs"), exist_ok=True)

def new_run_dir():
    ensure_runs_dir()
    run_tag = time.strftime("run_%Y%m%d_%H%M%S")
    p = os.path.join(repo_root(), "state", "runs", run_tag)
    os.makedirs(p, exist_ok=True)
    return p

# ─────────────────────────────────────────────────────────────
# ORCHESTRATOR LAUNCH (UI NEVER RUNS GIT)
# ─────────────────────────────────────────────────────────────
def run_orchestrator(repo_url: str, out_run_dir: str):
    # Dev: sys.executable=python.exe ; Frozen: sys.executable=IceCrawler.exe runtime
    temp_dir = os.path.join(repo_root(), "state", "_temp_repo")
    cmd = [sys.executable, "-m", "engine.orchestrator", repo_url, out_run_dir, "50", "120", temp_dir]
    p = subprocess.run(
        cmd,
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # Always capture UI-level stdout for postmortem
    try:
        open(os.path.join(out_run_dir, "ui_stdout.txt"), "w", encoding="utf-8").write(p.stdout or "")
        open(os.path.join(out_run_dir, "ui_rc.txt"), "w", encoding="utf-8").write(str(p.returncode))
    except:
        pass
    return p.returncode

# ─────────────────────────────────────────────────────────────
# PHOTO-LOCK STYLING (Tkinter only; no external deps)
# ─────────────────────────────────────────────────────────────
def apply_photo_lock_style(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    style.configure("TFrame", background="#0b1116")
    style.configure("TLabel", background="#0b1116", foreground="#d9f2ff", font=("Segoe UI", 11))
    style.configure("Title.TLabel", foreground="#e9fbff", font=("Segoe UI Semibold", 20))
    style.configure("Sub.TLabel", foreground="#8fb8c9", font=("Segoe UI", 10))

    style.configure("Phase.TLabel", foreground="#8fb8c9", font=("Segoe UI Semibold", 13))
    style.configure("Locked.TLabel", foreground="#6fe7ff", font=("Segoe UI Semibold", 13))

    style.configure("TButton", font=("Segoe UI Semibold", 11))
    style.map("TButton", foreground=[("disabled", "#5a6b74")])

    style.configure("TEntry", fieldbackground="#0f171e", foreground="#ffffff")
    style.configure("TProgressbar", thickness=14)

class IceCrawlerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ICE-CRAWLER ❄")
        self.geometry("980x860")
        self.configure(bg="#0b1116")

        apply_photo_lock_style(self)

        self.q = queue.Queue()
        self.running = False

        self.phase_truth = {p: False for p in PHASES}
        self.last_events = ""
        self.run_path = read_latest_run_path()

        self._build()
        self.after(200, self._animate)
        self.after(350, self._pump)

        # initial load
        self._refresh_from_fossils(force=True)

    def _build(self):
        # Header
        header = ttk.Frame(self, padding=18)
        header.pack(fill="x")

        ttl = ttk.Label(header, text="ICE-CRAWLER", style="Title.TLabel")
        ttl.pack(anchor="w")
        sub = ttk.Label(header, text="Event-Truth Ladder • Photo-Lock UI • Fossil Reader", style="Sub.TLabel")
        sub.pack(anchor="w", pady=(2,0))

        # Input row
        row = ttk.Frame(self, padding=(18, 0, 18, 8))
        row.pack(fill="x")

        self.url_entry = ttk.Entry(row, width=78)
        self.url_entry.pack(side="left", padx=(0,10), ipady=6)
        self.url_entry.insert(0, PLACEHOLDER)
        self._placeholder_active = True

        def on_focus_in(_):
            if self._placeholder_active:
                self.url_entry.delete(0, "end")
                self._placeholder_active = False

        def on_focus_out(_):
            if not self.url_entry.get().strip():
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, PLACEHOLDER)
                self._placeholder_active = True

        self.url_entry.bind("<FocusIn>", on_focus_in)
        self.url_entry.bind("<FocusOut>", on_focus_out)

        self.submit_btn = ttk.Button(row, text="Run", command=self.on_submit)
        self.submit_btn.pack(side="left")

        self.open_btn = ttk.Button(row, text="Open Run Folder", command=self.open_run_folder)
        self.open_btn.pack(side="left", padx=(10,0))

        # Ladder
        ladder = ttk.Frame(self, padding=18)
        ladder.pack(fill="x")

        self.phase_labels = {}
        for p in PHASES:
            lbl = ttk.Label(ladder, text=f"⬤ {p}", style="Phase.TLabel")
            lbl.pack(anchor="w", pady=3)
            self.phase_labels[p] = lbl

        # Progress
        prog = ttk.Frame(self, padding=(18,0,18,0))
        prog.pack(fill="x")
        self.progress = ttk.Progressbar(prog, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(4,12))

        # Output panes
        panes = ttk.Frame(self, padding=(18, 0, 18, 18))
        panes.pack(fill="both", expand=True)

        self.event_view = tk.Text(panes, height=16, bg="#0f171e", fg="#d9f2ff",
                                  insertbackground="#d9f2ff", wrap="word", relief="flat")
        self.event_view.pack(fill="both", expand=True, pady=(0,10))

        self.output_box = tk.Text(panes, height=6, bg="#0f171e", fg="#d9f2ff",
                                  insertbackground="#d9f2ff", wrap="word", relief="flat")
        self.output_box.pack(fill="x")

    # ─────────────────────────────────────────────
    # LADDER ANIMATION (only unfinished)
    # ─────────────────────────────────────────────
    def _animate(self):
        pulse = int(time.time() * 8) % 16
        glow = "⬤" if pulse < 8 else "◉"
        for p in PHASES:
            if not self.phase_truth[p]:
                self.phase_labels[p].configure(text=f"{glow} {p}")
        self.after(200, self._animate)

    def _lock(self, phase):
        if self.phase_truth.get(phase):
            return
        self.phase_truth[phase] = True
        self.phase_labels[phase].configure(text=f"✓ {phase}", style="Locked.TLabel")

    def _set_progress_from_events(self, events: str):
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self.progress["value"] = 100
        elif "CRYSTAL_VERIFIED" in events:
            self.progress["value"] = 85
        elif "GLACIER_VERIFIED" in events:
            self.progress["value"] = 55
        elif "FROST_VERIFIED" in events:
            self.progress["value"] = 25
        else:
            self.progress["value"] = 10

    def _refresh_from_fossils(self, force=False):
        if not self.run_path:
            self.event_view.delete("1.0","end")
            self.event_view.insert("end", "No run selected yet.\nRun once or set ui/latest_run_path.txt.\n")
            return

        events = read_events(self.run_path)
        if (not force) and (events == self.last_events):
            return

        self.last_events = events

        if "FROST_VERIFIED" in events:   self._lock("Frost")
        if "GLACIER_VERIFIED" in events: self._lock("Glacier")
        if "CRYSTAL_VERIFIED" in events: self._lock("Crystal")
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self._lock("Residue")

        self._set_progress_from_events(events)

        self.event_view.delete("1.0","end")
        self.event_view.insert("end", events[-2200:] if events else "(ui_events.jsonl not found yet)\n")

        # Artifact pointers (read-only)
        ai_path = read_text(os.path.join(self.run_path, "ai_handoff_path.txt")).strip()
        seal    = read_text(os.path.join(self.run_path, "root_seal.txt")).strip()

        self.output_box.delete("1.0","end")
        self.output_box.insert("end", f"Run: {self.run_path}\n")
        if ai_path:
            self.output_box.insert("end", f"\nAI Handoff:\n{ai_path}\n")
        if seal:
            self.output_box.insert("end", f"\nSeal:\n{seal}\n")


    def _reset_phase_ladder(self):
        self.phase_truth = {p: False for p in PHASES}
        for p in PHASES:
            self.phase_labels[p].configure(text=f"⬤ {p}", style="Phase.TLabel")

    def open_run_folder(self):
        if self.run_path and os.path.exists(self.run_path):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(self.run_path)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", self.run_path])
                else:
                    subprocess.Popen(["xdg-open", self.run_path])
            except Exception as e:
                messagebox.showerror("ICE-CRAWLER", str(e))
        else:
            messagebox.showinfo("ICE-CRAWLER", "No run folder yet.")

    # ─────────────────────────────────────────────
    # SUBMIT (spawns orchestrator; still fossil-driven UI updates)
    # ─────────────────────────────────────────────
    def on_submit(self):
        repo_url = self.url_entry.get().strip()

        if (not repo_url) or (repo_url == PLACEHOLDER):
            messagebox.showerror("ICE-CRAWLER", "Repo URL required.")
            return

        if self.running:
            return

        self.running = True
        self.submit_btn.configure(state="disabled")
        self.progress["value"] = 12

        run_dir = new_run_dir()
        write_latest_run_path(run_dir)
        self.run_path = run_dir
        self.last_events = ""
        self._reset_phase_ladder()

        def work():
            try:
                rc = run_orchestrator(repo_url, run_dir)
                self.q.put(("DONE", rc, run_dir))
            except Exception:
                self.q.put(("ERR", -1, traceback.format_exc()))

        threading.Thread(target=work, daemon=True).start()

    # ─────────────────────────────────────────────
    # PUMP LOOP (reads fossils only; no flicker)
    # ─────────────────────────────────────────────
    def _pump(self):
        try:
            while True:
                tag, rc, payload = self.q.get_nowait()
                self.running = False
                self.submit_btn.configure(state="normal")
                if tag == "ERR":
                    messagebox.showerror("ICE-CRAWLER", f"Run error:\n\n{payload}")
        except queue.Empty:
            pass

        self._refresh_from_fossils(force=False)
        self.after(350, self._pump)

if __name__ == "__main__":
    IceCrawlerUI().mainloop()
