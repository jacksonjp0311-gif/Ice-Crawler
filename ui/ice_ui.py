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
    if is_frozen():
        cmd = [sys.executable, "--orchestrator", repo_url, out_run_dir, "50", "120", temp_dir]
    else:
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


def apply_window_icon(root: tk.Tk):
    """Best-effort app icon loader (snowflake)."""
    try:
        ico = os.path.join(ui_dir(), "assets", "snowflake.ico")
        png = os.path.join(ui_dir(), "assets", "snowflake.png")
        if os.path.exists(ico):
            root.iconbitmap(ico)
            return
        if os.path.exists(png):
            img = tk.PhotoImage(file=png)
            root.iconphoto(True, img)
            root._icon_ref = img
    except Exception:
        pass

def apply_photo_lock_style(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    style.configure("TFrame", background="#0b1116")
    style.configure("TLabel", background="#071225", foreground="#63dcff", font=("Segoe UI", 11))
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
        self.geometry("1060x760")
        self.configure(bg="#051024")

        apply_window_icon(self)
        apply_photo_lock_style(self)

        self.q = queue.Queue()
        self.running = False

        self.phase_truth = {p: False for p in PHASES}
        self.last_events = ""
        self.run_path = read_latest_run_path()

        self._phase_dots = {}
        self._build()
        self.after(200, self._animate)
        self.after(350, self._pump)

        # initial load
        self._refresh_from_fossils(force=True)

    def _build(self):
        root = tk.Frame(self, bg="#051024")
        root.pack(fill="both", expand=True)

        header = tk.Frame(root, bg="#051024")
        header.pack(fill="x", padx=22, pady=(18, 6))
        tk.Label(header, text="ICE-CRAWLER", fg="#63dcff", bg="#051024", font=("Segoe UI", 36, "bold")).pack(anchor="w")
        tk.Label(header, text="Event-Truth Ladder • Photo-Lock UI • Fossil Reader", fg="#1fbfff", bg="#051024", font=("Segoe UI", 20)).pack(anchor="w")

        # Input row
        row = tk.Frame(root, bg="#051024")
        row.pack(fill="x", padx=22, pady=(8, 14))

        self.url_entry = tk.Entry(row, width=64, bg="#071a35", fg="#35c6ff", insertbackground="#63dcff", relief="solid", bd=2, font=("Segoe UI", 18))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 14), ipady=8)
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

        self.submit_btn = tk.Button(row, text="▼  RUN ICE CRAWLER", command=self.on_submit, bg="#0f355c", fg="#ffd078", activebackground="#164878", activeforeground="#ffd078", relief="flat", padx=14, pady=10, font=("Segoe UI", 12, "bold"))
        self.submit_btn.pack(side="left")

        # Ladder
        ladder = tk.Frame(root, bg="#051024")
        ladder.pack(fill="x", padx=22, pady=(2, 14))

        self.phase_labels = {}
        for p in PHASES:
            phase_row = tk.Frame(ladder, bg="#051024")
            phase_row.pack(anchor="w", pady=5)
            dot = tk.Label(phase_row, text="○", fg="#63dcff", bg="#051024", font=("Segoe UI", 24, "bold"))
            dot.pack(side="left")
            lbl = tk.Label(phase_row, text=p, fg="#63dcff", bg="#051024", font=("Segoe UI", 24, "bold"))
            lbl.pack(side="left", padx=(10, 0))
            self.phase_labels[p] = lbl
            self._phase_dots[p] = dot

        # Progress
        prog = tk.Frame(root, bg="#051024")
        prog.pack(fill="x", padx=22, pady=(0, 14))
        self.progress = ttk.Progressbar(prog, mode="determinate", maximum=100, style="TProgressbar")
        self.progress.pack(fill="x")

        # Output panes
        lower = tk.Frame(root, bg="#051024")
        lower.pack(fill="x", padx=22, pady=(8, 0))
        tk.Label(lower, text="All that remains...", fg="#63dcff", bg="#051024", font=("Segoe UI", 28, "bold")).pack(anchor="w")
        self.artifact_link = tk.Label(lower, text="Artifact path will appear after Crystal lock.", fg="#8adfff", bg="#051024", cursor="hand2", font=("Consolas", 14, "underline"))
        self.artifact_link.pack(anchor="w", pady=(8, 8))
        self.artifact_link.bind("<Button-1>", lambda _e: self.open_artifact_folder())

        self.status_line = tk.Label(root, text="Run: waiting", fg="#8adfff", bg="#051024", font=("Consolas", 15))
        self.status_line.pack(side="bottom", anchor="w", padx=22, pady=(6, 12))

        self.event_view = tk.Text(root, height=2, bg="#051024", fg="#051024", relief="flat", borderwidth=0)
        self.output_box = tk.Text(root, height=2, bg="#051024", fg="#051024", relief="flat", borderwidth=0)

    # ─────────────────────────────────────────────
    # LADDER ANIMATION (only unfinished)
    # ─────────────────────────────────────────────
    def _animate(self):
        pulse = int(time.time() * 8) % 16
        glow = "⬤" if pulse < 8 else "◉"
        for p in PHASES:
            if not self.phase_truth[p]:
                self._phase_dots[p].configure(text=glow)
        self.after(200, self._animate)

    def _lock(self, phase):
        if self.phase_truth.get(phase):
            return
        self.phase_truth[phase] = True
        self._phase_dots[phase].configure(text="●", fg="#35ffb2")
        self.phase_labels[phase].configure(fg="#35ffb2")

    def _set_progress_from_events(self, events: str):
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self.progress["value"] = 100
        elif "CRYSTAL_VERIFIED" in events:
            self.progress["value"] = 85
        elif "CRYSTAL_PENDING" in events:
            self.progress["value"] = 70
        elif "GLACIER_VERIFIED" in events:
            self.progress["value"] = 55
        elif "GLACIER_PENDING" in events:
            self.progress["value"] = 40
        elif "FROST_VERIFIED" in events:
            self.progress["value"] = 25
        elif "FROST_PENDING" in events:
            self.progress["value"] = 18
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
        seal = ""
        if ai_path:
            seal = read_text(os.path.join(ai_path, "root_seal.txt")).strip()
        if not seal:
            seal = read_text(os.path.join(self.run_path, "root_seal.txt")).strip()

        self.output_box.delete("1.0","end")
        self.output_box.insert("end", f"Run: {self.run_path}\n")
        self.status_line.configure(text=f"Run: {self.run_path}")
        if ai_path:
            self.output_box.insert("end", f"\nAI Handoff:\n{ai_path}\n")
            self.artifact_link.configure(text=ai_path, fg="#8adfff")
        else:
            self.artifact_link.configure(text="Artifact path will appear after Crystal lock.", fg="#8adfff")
        if seal:
            self.output_box.insert("end", f"\nSeal:\n{seal}\n")


    def _reset_phase_ladder(self):
        self.phase_truth = {p: False for p in PHASES}
        for p in PHASES:
            self.phase_labels[p].configure(fg="#63dcff")
            self._phase_dots[p].configure(text="○", fg="#63dcff")

    def open_artifact_folder(self):
        if not self.run_path:
            messagebox.showinfo("ICE-CRAWLER", "No run folder yet.")
            return
        ai_path = read_text(os.path.join(self.run_path, "ai_handoff_path.txt")).strip()
        if ai_path and os.path.exists(ai_path):
            target = ai_path
        elif self.run_path and os.path.exists(self.run_path):
            target = self.run_path
        else:
            messagebox.showinfo("ICE-CRAWLER", "No artifact path yet.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(target)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
        except Exception as e:
            messagebox.showerror("ICE-CRAWLER", str(e))

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
        self.submit_btn.configure(state="disabled", text="RUNNING...")
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
                self.submit_btn.configure(state="normal", text="▼  RUN ICE CRAWLER")
                if tag == "ERR":
                    messagebox.showerror("ICE-CRAWLER", f"Run error:\n\n{payload}")
        except queue.Empty:
            pass

        self._refresh_from_fossils(force=False)
        self.after(350, self._pump)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--orchestrator":
        root = repo_root()
        if root not in sys.path:
            sys.path.insert(0, root)
        from engine.orchestrator import main as orchestrator_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        raise SystemExit(orchestrator_main())
    IceCrawlerUI().mainloop()
