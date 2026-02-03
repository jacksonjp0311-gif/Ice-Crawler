# ui/ice_ui.py
# ❄ ICE-CRAWLER UI v5.0C — FROZEN ROOT TRUTH LOCK (PUBLIC EXE STABILITY)

import os, sys, threading, queue, time, subprocess, traceback
import tkinter as tk
from tkinter import ttk, messagebox

from design.layout import apply_style, build_surface

PHASES = ["Frost","Glacier","Crystal","Residue"]
PLACEHOLDER = "Paste a GitHub URL (recommended) or repo URL..."

def _is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def compute_repo_root():
    """
    Dev:    repo root = ../ (from ui/)
    Frozen: repo root = folder containing IceCrawler.exe (NOT _MEIPASS temp)
    """
    if _is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def ensure_dirs(repo_root):
    os.makedirs(os.path.join(repo_root, "state", "runs"), exist_ok=True)

def run_orchestrator(repo_root, repo_url):
    """
    Always run orchestrator through the current interpreter:
      - Dev:    sys.executable == python.exe
      - Frozen: sys.executable == IceCrawler.exe embedded runtime
    IMPORTANT:
      - cwd MUST be repo_root so relative paths + outputs land next to exe/repo.
    """
    ensure_dirs(repo_root)

    state_dir = os.path.join(repo_root, "state", "runs")
    run_tag   = time.strftime("run_%Y%m%d_%H%M%S")
    state_run = os.path.join(state_dir, run_tag)
    os.makedirs(state_run, exist_ok=True)

    cmd = [sys.executable, "-m", "engine.orchestrator", repo_url, state_run, "50", "120"]

    p = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # Always emit a local trace for frozen debugging
    try:
        open(os.path.join(state_run, "ui_stdout.txt"), "w", encoding="utf-8").write(p.stdout or "")
        open(os.path.join(state_run, "ui_rc.txt"), "w", encoding="utf-8").write(str(p.returncode))
    except:
        pass

    return p.returncode, state_run

def read_events(state_run):
    ev = os.path.join(state_run, "ui_events.jsonl")
    if not os.path.exists(ev):
        return ""
    try:
        return open(ev, "r", encoding="utf-8").read()
    except:
        return ""

class IceCrawlerUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ICE-CRAWLER ❄")
        self.geometry("950x880")

        # ✅ ROOT TRUTH: frozen => exe folder, dev => repo root
        self.repo_root = compute_repo_root()

        self.q = queue.Queue()
        self.state_run = None
        self.last_events = ""

        # Truth-lock completion
        self.phase_truth = {p: False for p in PHASES}

        # Running gate (prevents spam + “buggy” re-enable)
        self.running = False

        style = ttk.Style()
        apply_style(style)
        build_surface(self, PHASES)

        # --- URL Placeholder Truth ---
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, PLACEHOLDER)
        self.url_entry.configure(foreground="#7aa7b7")

        def on_focus_in(_):
            cur = self.url_entry.get()
            if cur.strip() == PLACEHOLDER:
                self.url_entry.delete(0, "end")
                self.url_entry.configure(foreground="#ffffff")
            self.url_entry.select_range(0, "end")

        def on_focus_out(_):
            cur = self.url_entry.get().strip()
            if not cur:
                self.url_entry.delete(0, "end")
                self.url_entry.insert(0, PLACEHOLDER)
                self.url_entry.configure(foreground="#7aa7b7")

        self.url_entry.bind("<FocusIn>", on_focus_in)
        self.url_entry.bind("<FocusOut>", on_focus_out)

        # Animation pulse
        self.pulse = 0
        self.after(120, self._animate)
        self.after(250, self._pump)

        # Surface info line (helps public users)
        try:
            self.output_box.delete("1.0", "end")
            self.output_box.insert("end", f"Root: {self.repo_root}\nFrozen: {_is_frozen()}\n")
        except:
            pass

    # ─────────────────────────────────────────────
    # LADDER ANIMATION (ONLY UNFINISHED)
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
        if self.phase_truth.get(phase):
            return
        self.phase_truth[phase] = True
        lbl = self.phase_labels[phase]
        lbl.config(text=f"✓ {phase}", foreground="#6fe7ff")

    def open_artifact(self):
        if self.state_run and os.path.exists(self.state_run):
            os.startfile(self.state_run)
        else:
            messagebox.showinfo("ICE-CRAWLER", "No artifact folder yet.")

    # ─────────────────────────────────────────────
    # SUBMIT
    # ─────────────────────────────────────────────
    def on_submit(self):
        repo_url = self.url_entry.get().strip()

        if not repo_url or repo_url == PLACEHOLDER:
            messagebox.showerror("ICE-CRAWLER", "Repo URL required.")
            return

        if self.running:
            return

        self.running = True
        self.submit_btn.config(state="disabled")
        self.progress["value"] = 10

        def work():
            try:
                rc, state_run = run_orchestrator(self.repo_root, repo_url)
                self.q.put(("DONE", rc, state_run))
            except Exception:
                self.q.put(("ERR", -1, traceback.format_exc()))

        threading.Thread(target=work, daemon=True).start()

    # ─────────────────────────────────────────────
    # PUMP LOOP (NO FLICKER + TRUE GATING)
    # ─────────────────────────────────────────────
    def _pump(self):
        # handle completion/errors
        try:
            while True:
                tag, rc, payload = self.q.get_nowait()
                if tag == "DONE":
                    self.state_run = payload
                    self.running = False
                    self.submit_btn.config(state="normal")
                else:
                    self.running = False
                    self.submit_btn.config(state="normal")
                    messagebox.showerror("ICE-CRAWLER", f"Run error:\n\n{payload}")
        except queue.Empty:
            pass

        # update UI from events only when changed
        if self.state_run:
            events = read_events(self.state_run)

            if events != self.last_events:
                self.last_events = events

                if "FROST_VERIFIED" in events:   self._lock_phase("Frost")
                if "GLACIER_VERIFIED" in events: self._lock_phase("Glacier")
                if "CRYSTAL_VERIFIED" in events: self._lock_phase("Crystal")
                if "RESIDUE_LOCK" in events:     self._lock_phase("Residue")

                # progress truth ladder
                if "RESIDUE_LOCK" in events:
                    self.progress["value"] = 100
                elif "CRYSTAL_VERIFIED" in events:
                    self.progress["value"] = 85
                elif "GLACIER_VERIFIED" in events:
                    self.progress["value"] = 55
                elif "FROST_VERIFIED" in events:
                    self.progress["value"] = 25
                else:
                    self.progress["value"] = 15

                # artifact proof
                proof = os.path.join(self.state_run, "ai_handoff_path.txt")
                if os.path.exists(proof):
                    path = open(proof, "r", encoding="utf-8").read().strip()
                    self.output_box.delete("1.0", "end")
                    self.output_box.insert("end", path)

                # fossil viewer tail
                self.event_view.delete("1.0", "end")
                self.event_view.insert("end", events[-1600:])

        self.after(250, self._pump)

if __name__ == "__main__":
    IceCrawlerUI().mainloop()
