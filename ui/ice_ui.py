# ui/ice_ui.py
# ❄ ICE-CRAWLER UI — Event-Truth + Photo-Lock Control Surface

import os
import queue
import subprocess
import sys
import threading
import time
import traceback
import tkinter as tk
from tkinter import messagebox

PHASES = ["Frost", "Glacier", "Crystal", "Residue"]
PLACEHOLDER = "Paste a GitHub URL (recommended) or repo URL..."
EVENT_FILE = "ui_events.jsonl"

BG = "#050b14"
PANEL = "#071427"
BLUE = "#00d5ff"
BLUE2 = "#4fe3ff"
ORANGE = "#ff9b1a"
ORANGE2 = "#ff6a00"
GREEN = "#3cffbc"
DIM = "#6fb9c9"


def is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def repo_root():
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
    except Exception:
        return None


def write_latest_run_path(run_path: str):
    try:
        open(latest_run_path_file(), "w", encoding="utf-8").write(run_path or "")
    except Exception:
        pass


def read_text(path: str) -> str:
    if not path or (not os.path.exists(path)):
        return ""
    try:
        return open(path, "r", encoding="utf-8").read()
    except Exception:
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


def run_orchestrator(repo_url: str, out_run_dir: str):
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
        text=True,
    )
    try:
        open(os.path.join(out_run_dir, "ui_stdout.txt"), "w", encoding="utf-8").write(p.stdout or "")
        open(os.path.join(out_run_dir, "ui_rc.txt"), "w", encoding="utf-8").write(str(p.returncode))
    except Exception:
        pass
    return p.returncode


class GlowTriangleButton(tk.Canvas):
    def __init__(self, master, command=None, w=122, h=96, **kw):
        super().__init__(master, width=w, height=h, bg=BG, highlightthickness=0, bd=0, **kw)
        self.w = w
        self.h = h
        self.command = command
        self.hover = False
        self.pressed = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_down)
        self.bind("<ButtonRelease-1>", self._on_up)
        self._draw()

    def set_enabled(self, enabled: bool):
        if enabled:
            self.configure(state="normal")
        else:
            self.configure(state="disabled")
        self._draw()

    def _on_enter(self, _):
        self.hover = True
        self._draw()

    def _on_leave(self, _):
        self.hover = False
        self.pressed = False
        self._draw()

    def _on_down(self, _):
        self.pressed = True
        self._draw()

    def _on_up(self, e):
        was_pressed = self.pressed
        self.pressed = False
        self._draw()
        if was_pressed and 0 <= e.x <= self.w and 0 <= e.y <= self.h and self.command:
            self.command()

    def _draw(self):
        self.delete("all")

        if str(self.cget("state")) == "disabled":
            edge_outer = "#604522"
            edge_inner = "#25526a"
            fill = "#0f5e76"
        else:
            edge_outer = ORANGE2
            edge_inner = BLUE
            fill = "#08b0d8" if (self.hover or self.pressed) else "#0a8fb2"

        left_x, right_x, top_y, bottom_y = 16, self.w - 16, 14, self.h - 14
        mid_x = self.w // 2

        for i in range(9):
            self.create_polygon(
                left_x - i, top_y + i,
                right_x + i, top_y + i,
                mid_x, bottom_y + i,
                fill="",
                outline=edge_outer,
                width=2,
            )

        for i in range(7):
            self.create_polygon(
                left_x + 10 - i, top_y + 14 + i,
                right_x - 10 + i, top_y + 14 + i,
                mid_x, bottom_y - 8 + i,
                fill="",
                outline=edge_inner,
                width=2,
            )

        self.create_polygon(
            left_x + 12, top_y + 18,
            right_x - 12, top_y + 18,
            mid_x, bottom_y - 12,
            fill=fill,
            outline=BLUE2,
            width=2,
        )


class IceCrawlerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ICE-CRAWLER ❄")
        self.geometry("1120x760")
        self.minsize(980, 700)
        self.configure(bg=BG)

        self._bg_image = None
        self._status_after = None
        self._phase_dots = {}
        self.q = queue.Queue()
        self.running = False
        self.phase_truth = {p: False for p in PHASES}
        self.last_events = ""
        self.run_path = read_latest_run_path()

        self._build()

        self.after(200, self._animate)
        self.after(300, self._pump)
        self._refresh_from_fossils(force=True)

    def _build(self):
        bg = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_canvas = bg
        self._paint_background()
        self.bind("<Configure>", lambda _e: self._paint_background())

        shell = tk.Frame(self, bg=BG)
        shell.place(x=0, y=0, relwidth=1, relheight=1)

        header = tk.Frame(shell, bg=BG)
        header.pack(fill="x", padx=22, pady=(16, 2))
        tk.Label(header, text="ICE-CRAWLER", fg=BLUE2, bg=BG, font=("Segoe UI", 28, "bold")).pack(anchor="w")
        tk.Label(header, text="Event-Truth Ladder • Photo-Lock UI • Fossil Reader", fg=BLUE, bg=BG, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        top = tk.Frame(shell, bg=BG)
        top.pack(fill="x", padx=22, pady=(10, 10))

        self.url_entry = tk.Entry(top, bg=PANEL, fg=DIM, insertbackground=BLUE2, relief="flat", font=("Consolas", 14))
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.url_entry.insert(0, PLACEHOLDER)
        self._placeholder_active = True
        self.url_entry.bind("<FocusIn>", self._on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_focus_out)

        tri = tk.Frame(top, bg=BG)
        tri.pack(side="left", padx=(18, 0))
        self.submit_btn = GlowTriangleButton(tri, command=self.on_submit, w=96, h=78)
        self.submit_btn.pack()
        self.submit_lbl = tk.Label(
            tri,
            text="PRESS TO SUBMIT\nTO ICE CRAWLER",
            fg=ORANGE,
            bg=BG,
            justify="center",
            font=("Segoe UI", 10, "bold"),
        )
        self.submit_lbl.pack(pady=(6, 0))

        phase_block = tk.Frame(shell, bg=BG)
        phase_block.pack(fill="x", padx=22, pady=(4, 8))

        self.phase_labels = {}
        for p in PHASES:
            row = tk.Frame(phase_block, bg=BG)
            row.pack(anchor="w", pady=2)
            dot = tk.Label(row, text="○", fg=BLUE2, bg=BG, font=("Segoe UI", 18, "bold"))
            dot.pack(side="left")
            lbl = tk.Label(row, text=p, fg=BLUE2, bg=BG, font=("Segoe UI", 18, "bold"))
            lbl.pack(side="left", padx=(8, 0))
            self._phase_dots[p] = dot
            self.phase_labels[p] = lbl

        self.progress_canvas = tk.Canvas(shell, height=18, bg=BG, highlightthickness=0, bd=0)
        self.progress_canvas.pack(fill="x", padx=22, pady=(2, 10))
        self._draw_progress(0)

        lower = tk.Frame(shell, bg=BG)
        lower.pack(fill="x", padx=22, pady=(0, 2))
        tk.Label(lower, text="All that remains...", fg=BLUE2, bg=BG, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        self.artifact_link = tk.Label(
            lower,
            text="Artifact path will appear after Crystal lock.",
            fg=BLUE2,
            bg=BG,
            cursor="hand2",
            font=("Consolas", 12, "underline"),
        )
        self.artifact_link.pack(anchor="w", pady=(6, 0))
        self.artifact_link.bind("<Button-1>", lambda _e: self.open_artifact_folder())

        self.status_line = tk.Label(shell, text="Run: waiting", fg=BLUE2, bg=BG, font=("Consolas", 12))
        self.status_line.pack(side="bottom", anchor="w", padx=22, pady=(6, 10))

    def _paint_background(self):
        c = self.bg_canvas
        c.delete("all")
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)

        bg_path = os.path.join(ui_dir(), "assets", "background.png")
        if os.path.exists(bg_path):
            try:
                self._bg_image = tk.PhotoImage(file=bg_path)
                c.create_image(0, 0, image=self._bg_image, anchor="nw")
                c.create_rectangle(0, 0, w, h, fill="#000000", stipple="gray50", outline="")
                return
            except Exception:
                self._bg_image = None

        for i in range(0, h, 3):
            blend = int(10 + (i / h) * 30)
            color = f"#{3:02x}{10+blend:02x}{30+blend:02x}"
            c.create_line(0, i, w, i, fill=color)

        for y in [170, 420, 700]:
            c.create_line(0, y, w, y, fill="#0db7ff", width=2)
            c.create_line(0, y + 2, w, y + 2, fill="#094062", width=2)

    def _on_url_focus_in(self, _):
        if self._placeholder_active:
            self.url_entry.delete(0, "end")
            self.url_entry.configure(fg=BLUE2)
            self._placeholder_active = False

    def _on_url_focus_out(self, _):
        if not self.url_entry.get().strip():
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, PLACEHOLDER)
            self.url_entry.configure(fg=DIM)
            self._placeholder_active = True

    def _animate(self):
        glow = "◉" if int(time.time() * 6) % 2 == 0 else "○"
        for p in PHASES:
            if not self.phase_truth[p]:
                self._phase_dots[p].configure(text=glow)
        self.after(220, self._animate)

    def _lock(self, phase):
        if self.phase_truth.get(phase):
            return
        self.phase_truth[phase] = True
        self._phase_dots[phase].configure(text="●", fg=GREEN)
        self.phase_labels[phase].configure(fg=GREEN)

    def _set_progress_from_events(self, events: str):
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self._draw_progress(100)
        elif "CRYSTAL_VERIFIED" in events:
            self._draw_progress(85)
        elif "CRYSTAL_PENDING" in events:
            self._draw_progress(70)
        elif "GLACIER_VERIFIED" in events:
            self._draw_progress(55)
        elif "GLACIER_PENDING" in events:
            self._draw_progress(40)
        elif "FROST_VERIFIED" in events:
            self._draw_progress(25)
        elif "FROST_PENDING" in events:
            self._draw_progress(18)
        else:
            self._draw_progress(10)

    def _draw_progress(self, value: int):
        c = self.progress_canvas
        c.delete("all")
        w = max(c.winfo_width(), 50)
        h = max(c.winfo_height(), 10)
        c.create_rectangle(0, 2, w, h - 2, outline="#9d9c8f", width=2, fill="#111820")
        fill_w = int((value / 100) * (w - 4))
        if fill_w > 0:
            c.create_rectangle(2, 4, 2 + fill_w, h - 4, outline="", fill="#1eaad5")

    def _refresh_from_fossils(self, force=False):
        if not self.run_path:
            self.status_line.configure(text="Run: waiting")
            return

        events = read_events(self.run_path)
        if (not force) and (events == self.last_events):
            return

        self.last_events = events

        if "FROST_VERIFIED" in events:
            self._lock("Frost")
        if "GLACIER_VERIFIED" in events:
            self._lock("Glacier")
        if "CRYSTAL_VERIFIED" in events:
            self._lock("Crystal")
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self._lock("Residue")

        self._set_progress_from_events(events)

        ai_path = read_text(os.path.join(self.run_path, "ai_handoff_path.txt")).strip()
        self.status_line.configure(text=f"Run: {self.run_path}")
        if ai_path:
            self.artifact_link.configure(text=ai_path)
        else:
            self.artifact_link.configure(text="Artifact path will appear after Crystal lock.")

    def _reset_phase_ladder(self):
        self.phase_truth = {p: False for p in PHASES}
        for p in PHASES:
            self.phase_labels[p].configure(fg=BLUE2)
            self._phase_dots[p].configure(text="○", fg=BLUE2)
        self._draw_progress(8)
        self.artifact_link.configure(text="Artifact path will appear after Crystal lock.")

    def _flash_submit_label(self):
        if self.running:
            current = self.submit_lbl.cget("fg")
            self.submit_lbl.configure(fg=ORANGE2 if current == ORANGE else ORANGE)
            self._status_after = self.after(240, self._flash_submit_label)
        else:
            self.submit_lbl.configure(fg=ORANGE)

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

    def on_submit(self):
        repo_url = self.url_entry.get().strip()
        if (not repo_url) or (repo_url == PLACEHOLDER):
            messagebox.showerror("ICE-CRAWLER", "Repo URL required.")
            return

        if self.running:
            return

        self.running = True
        self.submit_btn.set_enabled(False)
        self.submit_lbl.configure(text="RUNNING...")
        self._flash_submit_label()

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

    def _pump(self):
        try:
            while True:
                tag, rc, payload = self.q.get_nowait()
                self.running = False
                self.submit_btn.set_enabled(True)
                self.submit_lbl.configure(text="PRESS TO SUBMIT\nTO ICE CRAWLER")
                if tag == "ERR":
                    messagebox.showerror("ICE-CRAWLER", f"Run error:\n\n{payload}")
                elif rc != 0:
                    messagebox.showerror("ICE-CRAWLER", f"Run failed with exit code {rc}.\nCheck ui_rc.txt/ui_stdout.txt in:\n{payload}")
        except queue.Empty:
            pass

        self._refresh_from_fossils(force=False)
        self.after(300, self._pump)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--orchestrator":
        root = repo_root()
        if root not in sys.path:
            sys.path.insert(0, root)
        from engine.orchestrator import main as orchestrator_main

        sys.argv = [sys.argv[0]] + sys.argv[2:]
        raise SystemExit(orchestrator_main())
    IceCrawlerUI().mainloop()
