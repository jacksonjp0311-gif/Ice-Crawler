# ui/ice_ui.py
# ❄ ICE-CRAWLER UI — Event-Truth + Photo-Lock Control Surface

import os
import queue
import random
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

STAGE_REVEALS = {
    "Frost": "signal detected",
    "Glacier": "structure stabilizing",
    "Crystal": "invariant sealed",
    "Residue": "artifact remains",
}


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




def _status_text_for_path(path: str, max_chars: int = 74) -> str:
    if not path:
        return "Run: waiting"
    p = str(path)
    if len(p) <= max_chars:
        return f"Run: {p}"
    return f"Run: ...{p[-(max_chars-8):]}"


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
    def __init__(self, master, command=None, w=104, h=86, **kw):
        super().__init__(master, width=w, height=h, bg=BG, highlightthickness=0, bd=0, **kw)
        self.w = w
        self.h = h
        self.command = command
        self.hover = False
        self.pressed = False
        self.vibe_phase = 0

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_down)
        self.bind("<ButtonRelease-1>", self._on_up)
        self._draw()

    def set_enabled(self, enabled: bool):
        self.configure(state="normal" if enabled else "disabled")
        self._draw()

    def _on_enter(self, _):
        self.hover = True
        self._draw()

    def _on_leave(self, _):
        self.hover = False
        self.pressed = False
        self.vibe_phase = 0
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

    def tick(self, enabled: bool):
        self.vibe_phase = (self.vibe_phase + 1) % 6 if enabled else 0
        self._draw()

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

        jitter = [-1, 0, 1, 0, -1, 1][self.vibe_phase] if str(self.cget("state")) != "disabled" else 0
        left_x, right_x, top_y, bottom_y = 15 + jitter, self.w - 15 + jitter, 10, self.h - 10
        mid_x = self.w // 2

        pulse_extra = 1 if self.vibe_phase in (1, 4) else 0

        for i in range(7 + pulse_extra):
            self.create_polygon(
                left_x - i, top_y + i,
                right_x + i, top_y + i,
                mid_x, bottom_y + i,
                fill="",
                outline=edge_outer,
                width=2,
            )

        for i in range(5):
            self.create_polygon(
                left_x + 8 - i, top_y + 11 + i,
                right_x - 8 + i, top_y + 11 + i,
                mid_x, bottom_y - 7 + i,
                fill="",
                outline=edge_inner,
                width=2,
            )

        self.create_polygon(
            left_x + 11, top_y + 14,
            right_x - 11, top_y + 14,
            mid_x, bottom_y - 10,
            fill=fill,
            outline=BLUE2,
            width=2,
        )


class IceCrawlerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ICE-CRAWLER ❄")
        self.geometry("1160x760")
        self.minsize(1000, 700)
        self.configure(bg=BG)

        self._bg_image = None
        self._phase_dots = {}
        self._stars = []
        self.phase_labels = {}

        self._bg_image = None
        self._status_after = None
        self._phase_dots = {}
        self.q = queue.Queue()
        self.running = False
        self.phase_truth = {p: False for p in PHASES}
        self.last_events = ""
        self.run_path = read_latest_run_path()

        self._phase_dots = {}
        self._build()

        self.after(200, self._animate)
        self.after(80, self._animate_stars)
        self.after(300, self._pump)
        self._refresh_from_fossils(force=True)

    def _build(self):
        self.bg_canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._paint_background()
        self._init_stars()
        self.bind("<Configure>", self._on_resize)

        shell = tk.Frame(self, bg=BG)
        shell.place(x=0, y=0, relwidth=1, relheight=1)

        header = tk.Frame(shell, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 4))
        title_row = tk.Frame(header, bg=BG)
        title_row.pack(anchor="w")
        tk.Label(title_row, text="ICE-CRAWLER", fg=BLUE2, bg=BG, font=("Segoe UI", 30, "bold")).pack(side="left")
        tk.Label(title_row, text="❄", fg=BLUE2, bg=BG, font=("Segoe UI", 22, "bold")).pack(side="left", padx=(10, 0))
        tk.Label(
            header,
            text="Event-Truth Ladder • Photo-Lock UI • Fossil Reader",
            fg=BLUE,
            bg=BG,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        top = tk.Frame(shell, bg=BG)
        top.pack(fill="x", padx=20, pady=(8, 10))

        self.url_entry = tk.Entry(top, bg=PANEL, fg=DIM, insertbackground=BLUE2, relief="flat", font=("Consolas", 14))
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=7)
        self.url_entry.insert(0, PLACEHOLDER)
        self._placeholder_active = True
        self.url_entry.bind("<FocusIn>", self._on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_focus_out)

        action_panel = tk.Frame(top, bg=BG)
        action_panel.pack(side="left", padx=(14, 0))

        button_row = tk.Frame(action_panel, bg=BG)
        button_row.pack(anchor="w")
        self.submit_btn = GlowTriangleButton(button_row, command=self.on_submit, w=104, h=86)
        self.submit_btn.pack(side="left")

        self.submit_lbl = tk.Label(
            button_row,
            text="PRESS TO SUBMIT\nTO ICE CRAWLER",
            fg=ORANGE,
            bg=BG,
            justify="left",
            font=("Segoe UI", 11, "bold"),
        )
        self.submit_lbl.pack(side="left", padx=(8, 0))

        self._submit_line_1 = tk.Frame(action_panel, bg=ORANGE, height=1, width=240)
        self._submit_line_1.pack(anchor="w", pady=(5, 0))
        self._submit_line_2 = tk.Frame(action_panel, bg=ORANGE, height=1, width=170)
        self._submit_line_2.pack(anchor="w", pady=(3, 0))

        phase_block = tk.Frame(shell, bg=BG)
        phase_block.pack(fill="x", padx=20, pady=(4, 6))

        self.phase_reveals = {}
        self.reveal_started = {p: False for p in PHASES}
        for p in PHASES:
            row = tk.Frame(phase_block, bg=BG)
            row.pack(anchor="w", pady=2)
            dot = tk.Label(row, text="○", fg=BLUE2, bg=BG, font=("Segoe UI", 24, "bold"))
            dot.pack(side="left")
            lbl = tk.Label(row, text=p, fg=BLUE2, bg=BG, font=("Segoe UI", 19, "bold"))
            lbl.pack(side="left", padx=(8, 8))
            reveal = tk.Label(row, text="", fg=ORANGE, bg=BG, font=("Segoe UI", 12, "italic"))
            reveal.pack(side="left")
            self._phase_dots[p] = dot
            self.phase_labels[p] = lbl
            self.phase_reveals[p] = reveal

        self.progress_canvas = tk.Canvas(shell, height=18, bg=BG, highlightthickness=0, bd=0)
        self.progress_canvas.pack(fill="x", padx=20, pady=(4, 10))
        self._draw_progress(0)

        lower = tk.Frame(shell, bg=BG)
        lower.pack(fill="x", padx=20, pady=(0, 2))
        tk.Label(lower, text="All that remains...", fg=ORANGE, bg=BG, font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.artifact_link = tk.Label(
            lower,
            text="Artifact path will appear after Crystal lock.",
            fg=BLUE2,
            bg=BG,
            cursor="hand2",
            font=("Consolas", 11, "underline"),
            wraplength=900,
            justify="left",
        )
        self.artifact_link.pack(anchor="w", pady=(6, 0))
        self.artifact_link.bind("<Button-1>", lambda _e: self.open_artifact_folder())

        self.status_line = tk.Label(shell, text="Run: waiting", fg=BLUE2, bg=BG, font=("Consolas", 10))
        self.status_line.pack(side="bottom", anchor="w", padx=20, pady=(6, 10))



    def _queue_reveal(self, phase: str):
        if self.reveal_started.get(phase):
            return
        self.reveal_started[phase] = True
        self.after(250, lambda: self._fade_in_reveal(phase, 0))

    def _fade_in_reveal(self, phase: str, step: int):
        reveal = self.phase_reveals.get(phase)
        if not reveal:
            return
        text = STAGE_REVEALS.get(phase, "")
        if not text:
            return
        reveal.configure(text=text)
        colors = ["#2b1b0d", "#5a3410", "#8a4f12", "#c66d18", ORANGE]
        idx = min(step, len(colors) - 1)
        reveal.configure(fg=colors[idx])
        if idx < len(colors) - 1:
            self.after(50, lambda: self._fade_in_reveal(phase, step + 1))

    def _on_resize(self, event):
        self._paint_background()
        if hasattr(self, "artifact_link"):
            width = max(getattr(event, "width", self.winfo_width()), 700)
            self.artifact_link.configure(wraplength=max(520, width - 240))

    def _paint_background(self):
        c = self.bg_canvas
        c.delete("bg")
        w = max(c.winfo_width(), 2)
        h = max(c.winfo_height(), 2)

        bg_path = os.path.join(ui_dir(), "assets", "background.png")
        if os.path.exists(bg_path):
            try:
                self._bg_image = tk.PhotoImage(file=bg_path)
                c.create_image(0, 0, image=self._bg_image, anchor="nw", tags="bg")
                c.create_rectangle(0, 0, w, h, fill="#000000", stipple="gray50", outline="", tags="bg")
                return
            except Exception:
                self._bg_image = None

        for i in range(0, h, 3):
            blend = int(10 + (i / h) * 30)
            color = f"#{3:02x}{10+blend:02x}{30+blend:02x}"
            c.create_line(0, i, w, i, fill=color, tags="bg")

        for y in [170, 420, 700]:
            c.create_line(0, y, w, y, fill="#0db7ff", width=2, tags="bg")
            c.create_line(0, y + 2, w, y + 2, fill="#094062", width=2, tags="bg")

    def _init_stars(self):
        self._stars = []
        w = max(self.bg_canvas.winfo_width(), 1160)
        h = max(self.bg_canvas.winfo_height(), 760)
        for _ in range(90):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.choice([1, 1, 1, 2])
            color = random.choice(["#a8ecff", "#6fdcff", "#f0ffff"])
            sid = self.bg_canvas.create_oval(x, y, x + size, y + size, fill=color, outline="", tags="star")
            self._stars.append({"id": sid, "x": x, "y": y, "size": size, "speed": random.uniform(0.08, 0.35)})

    def _animate_stars(self):
        if not self._stars:
            self._init_stars()
        h = max(self.bg_canvas.winfo_height(), 760)
        w = max(self.bg_canvas.winfo_width(), 1160)
        for s in self._stars:
            s["y"] += s["speed"]
            if s["y"] > h:
                s["y"] = 0
                s["x"] = random.randint(0, w)
            self.bg_canvas.coords(s["id"], s["x"], s["y"], s["x"] + s["size"], s["y"] + s["size"])
        self.after(80, self._animate_stars)

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

        if self.running:
            current = self.submit_lbl.cget("fg")
            self.submit_lbl.configure(fg=ORANGE2 if current == ORANGE else ORANGE)
        else:
            self.submit_lbl.configure(fg=ORANGE)

        self.submit_btn.tick(str(self.submit_btn.cget("state")) != "disabled")
        self.after(220, self._animate)

    def _lock(self, phase):
        if self.phase_truth.get(phase):
            return
        self.phase_truth[phase] = True
        self._phase_dots[phase].configure(text="●", fg=GREEN)
        self.phase_labels[phase].configure(fg=GREEN)
        self._queue_reveal(phase)

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

    def _status_text_for_run(self, run_path: str):
        approx_chars = max(44, int(self.winfo_width() / 13))
        return _status_text_for_path(run_path, max_chars=approx_chars)

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
        self.status_line.configure(text=self._status_text_for_run(self.run_path))
        if ai_path:
            self.artifact_link.configure(text=ai_path)
        else:
            self.artifact_link.configure(text="Artifact path will appear after Crystal lock.")

    def _reset_phase_ladder(self):
        self.phase_truth = {p: False for p in PHASES}
        for p in PHASES:
            self.phase_labels[p].configure(fg=BLUE2)
            self._phase_dots[p].configure(text="○", fg=BLUE2)
            if hasattr(self, "phase_reveals") and p in self.phase_reveals:
                self.phase_reveals[p].configure(text="", fg=BLUE2)
            if hasattr(self, "reveal_started"):
                self.reveal_started[p] = False
        self._draw_progress(8)
        self.artifact_link.configure(text="Artifact path will appear after Crystal lock.")

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
                if tag == "ERR":
                    messagebox.showerror("ICE-CRAWLER", f"Run error:\n\n{payload}")
                elif rc != 0:
                    messagebox.showerror(
                        "ICE-CRAWLER",
                        f"Run failed with exit code {rc}.\nCheck ui_rc.txt/ui_stdout.txt in:\n{payload}",
                    )
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
