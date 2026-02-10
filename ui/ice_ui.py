# ui/ice_ui.py
# ❄ ICE-CRAWLER UI — Event-Truth + Photo-Lock Control Surface

import math
import os
import queue
import subprocess
import sys
import threading
import time
import traceback
import tkinter as tk
from tkinter import messagebox

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ui.animations import (
    ExecutionTimeline,
    HandoffCompleteBadge,
    RitualTriangleButton,
    StageLadderAnimator,
    StatusIndicator,
    attach_snowflake,
)
from ui.hooks import CommandStreamHook

PHASES = ["Frost", "Glacier", "Crystal", "Residue"]
PLACEHOLDER = "Paste a GitHub URL (recommended) or repo URL..."
EVENT_FILE = "ui_events.jsonl"

BG = "#050b14"
PANEL = "#071427"
BLUE = "#00d5ff"
BLUE2 = "#4fe3ff"
ORANGE = "#ff9b1a"
ORANGE2 = "#ff6a00"
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


def run_orchestrator(repo_url: str, out_run_dir: str, stream_hook: CommandStreamHook | None = None):
    temp_dir = os.path.join(repo_root(), "state", "_temp_repo")
    if is_frozen():
        cmd = [sys.executable, "--orchestrator", repo_url, out_run_dir, "50", "120", temp_dir]
    else:
        cmd = [sys.executable, "-m", "engine.orchestrator", repo_url, out_run_dir, "50", "120", temp_dir]
    creationflags = 0
    startupinfo = None
    if sys.platform.startswith("win"):
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    if stream_hook is None:
        p = subprocess.run(
            cmd,
            cwd=repo_root(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=creationflags,
            startupinfo=startupinfo,
        )
        rc = p.returncode
        stdout = p.stdout or ""
    else:
        rc, stdout = stream_hook.run_subprocess(
            cmd,
            cwd=repo_root(),
            creationflags=creationflags,
            startupinfo=startupinfo,
        )
    try:
        open(os.path.join(out_run_dir, "ui_stdout.txt"), "w", encoding="utf-8").write(stdout)
        open(os.path.join(out_run_dir, "ui_rc.txt"), "w", encoding="utf-8").write(str(rc))
    except Exception:
        pass
    return rc


class IceCrawlerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ICE-CRAWLER ❄")
        self.geometry("1160x760")
        self.minsize(1000, 700)
        self.configure(bg=BG)

        self._bg_image = None
        self._phase_dots = {}
        self.phase_labels = {}
        self.phase_checks = {}
        self._bg_image = None
        self._status_after = None
        self.q = queue.Queue()
        self.running = False
        self.run_complete = False
        self.has_activity = False
        self.phase_truth = {p: False for p in PHASES}
        self.last_events = ""
        self.run_path = read_latest_run_path()
        self.stream_hook = None

        self._phase_dots = {}
        self._build()

        self.after(200, self._animate)
        self.after(300, self._pump)
        self._refresh_from_fossils(force=True)

    def _build(self):
        self.bg_canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._paint_background()
        self.bind("<Configure>", self._on_resize)

        shell = tk.Frame(self, bg=BG)
        shell.place(x=0, y=0, relwidth=1, relheight=1)

        header = tk.Frame(shell, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 4))
        title_row = tk.Frame(header, bg=BG)
        title_row.pack(fill="x")
        tk.Label(title_row, text="ICE-CRAWLER", fg=BLUE2, bg=BG, font=("Segoe UI", 30, "bold")).pack(side="left")
        self.snowflake_canvas = attach_snowflake(title_row, self)
        self.snowflake_canvas.pack(side="left", padx=(8, 0))
        self.status_indicator_label = tk.Label(
            title_row,
            text="STATUS: IDLE",
            fg=BLUE2,
            bg=BG,
            font=("Consolas", 12, "bold"),
        )
        self.status_indicator_label.pack(side="right")
        tk.Label(
            header,
            text="Event-Truth Ladder • Photo-Lock UI • Fossil Reader",
            fg=BLUE,
            bg=BG,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")
        self.status_indicator = StatusIndicator(self.status_indicator_label)

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
        self.submit_btn = RitualTriangleButton(button_row, command=self.on_submit, w=104, h=86)
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

        ladder_column = tk.Frame(phase_block, bg=BG)
        ladder_column.pack(side="left", anchor="n", pady=(28, 0))

        status_column = tk.Frame(phase_block, bg=BG)
        status_column.pack(side="left", anchor="n", padx=(24, 0))

        self.phase_reveals = {}
        self.reveal_started = {p: False for p in PHASES}
        for p in PHASES:
            row = tk.Frame(ladder_column, bg=BG)
            row.pack(anchor="w", pady=2)
            dot = tk.Label(row, text="○", fg=BLUE2, bg=BG, font=("Segoe UI", 24, "bold"))
            dot.pack(side="left")
            lbl = tk.Label(row, text=p, fg=BLUE2, bg=BG, font=("Segoe UI", 19, "bold"))
            lbl.pack(side="left", padx=(8, 8))
            check = tk.Label(row, text="", fg=BLUE2, bg=BG, font=("Segoe UI", 16, "bold"))
            check.pack(side="left", padx=(0, 8))
            reveal = tk.Label(row, text="", fg=ORANGE, bg=BG, font=("Segoe UI", 12, "italic"))
            reveal.pack(side="left")
            self._phase_dots[p] = dot
            self.phase_labels[p] = lbl
            self.phase_checks[p] = check
            self.phase_reveals[p] = reveal

        self.agent_status_row = tk.Frame(status_column, bg=BG)
        self.agent_status_row.pack(anchor="w", pady=(2, 8))
        self.agent_status_row.pack_forget()

        self.agent_frame = tk.Frame(self.agent_status_row, bg=BG, highlightbackground=BLUE2, highlightthickness=2)
        self.agent_label = tk.Label(
            self.agent_frame,
            text="AGENTS",
            fg=BLUE2,
            bg=BG,
            font=("Segoe UI", 12, "bold"),
        )
        self.agent_label.pack(padx=12, pady=6)
        self.agent_frame.pack(side="left")

        self.agent_state_frame = tk.Frame(self.agent_status_row, bg=BG, highlightbackground=BLUE2, highlightthickness=2)
        self.agent_state_label = tk.Label(
            self.agent_state_frame,
            text="AGENTS: NOT RUN",
            fg=BLUE2,
            bg=BG,
            font=("Segoe UI", 12, "bold"),
        )
        self.agent_state_label.pack(padx=12, pady=6)
        self.agent_state_frame.pack(side="left", padx=(10, 0))
        self.agent_visible = False
        self.agent_state = None

        self.handoff_badge = HandoffCompleteBadge(status_column, command=self.open_handoff_folder)
        self.handoff_badge.pack(anchor="w", pady=(0, 8))
        self.handoff_badge.pack_forget()
        self.handoff_visible = False

        self.progress_canvas = tk.Canvas(shell, height=18, bg=BG, highlightthickness=0, bd=0)
        self.progress_canvas.pack(fill="x", padx=20, pady=(4, 10))
        self._draw_progress(0)

        lower = tk.Frame(shell, bg=BG)
        lower.pack(fill="x", padx=20, pady=(0, 2))
        residue_row = tk.Frame(lower, bg=BG)
        residue_row.pack(fill="x", anchor="w")
        self.output_panel = tk.Frame(residue_row, bg=BG)
        self.output_panel.pack(side="left", fill="both", expand=True, anchor="w")
        tk.Label(self.output_panel, text="OUTPUT RESIDUE", fg=ORANGE, bg=BG, font=("Segoe UI", 14, "bold")).pack(
            anchor="w"
        )
        tk.Frame(self.output_panel, bg=ORANGE, height=2, width=220).pack(anchor="w", pady=(2, 6))
        self.artifact_link = tk.Label(
            self.output_panel,
            text="All that remains...",
            fg=BLUE2,
            bg=BG,
            cursor="hand2",
            font=("Consolas", 12),
            wraplength=900,
            justify="left",
            anchor="w",
        )
        self.artifact_link.pack(anchor="w", pady=(2, 8))
        self.artifact_link.bind("<Button-1>", lambda _e: self.open_artifact_folder())
        self.agent_residue_label = tk.Label(
            self.output_panel,
            text="",
            fg=BLUE2,
            bg=BG,
            font=("Consolas", 11, "bold"),
            justify="left",
            anchor="w",
        )
        self.agent_residue_label.pack(anchor="w", pady=(0, 8))
        self.agent_residue_label.pack_forget()
        self.agent_residue_state = None

        self.log_column = tk.Frame(residue_row, bg=BG)
        self.log_column.pack(side="right", anchor="n", padx=(14, 0))

        self.stream_panel = tk.Frame(self.log_column, bg=BG, highlightbackground=BLUE2, highlightthickness=1)
        self.stream_panel.pack(anchor="n", pady=(0, 12))
        self.stream_panel.configure(width=320, height=150)
        self.stream_panel.pack_propagate(False)
        tk.Label(self.stream_panel, text="CMD STREAM", fg=BLUE2, bg=BG, font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        self.stream_text = tk.Text(
            self.stream_panel,
            height=6,
            width=38,
            bg="#061729",
            fg=BLUE2,
            insertbackground=BLUE2,
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
        )
        self.stream_text.pack(anchor="w", padx=10, pady=(0, 10), fill="both", expand=True)
        self.stream_text.configure(state="disabled")

        self.cmd_panel = tk.Frame(self.log_column, bg=BG, highlightbackground=BLUE2, highlightthickness=1)
        self.cmd_panel.pack(anchor="n", pady=(0, 12))
        self.cmd_panel.configure(width=320, height=150)
        self.cmd_panel.pack_propagate(False)
        tk.Label(self.cmd_panel, text="CMD TRACE", fg=BLUE2, bg=BG, font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        self.cmd_text = tk.Text(
            self.cmd_panel,
            height=6,
            width=38,
            bg="#061729",
            fg=BLUE2,
            insertbackground=BLUE2,
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
        )
        self.cmd_text.pack(anchor="w", padx=10, pady=(0, 10), fill="both", expand=True)
        self.cmd_text.configure(state="disabled")

        self.log_panel = tk.Frame(self.log_column, bg=BG, highlightbackground=BLUE2, highlightthickness=1)
        self.log_panel.pack(anchor="n")
        self.log_panel.configure(width=320, height=150)
        self.log_panel.pack_propagate(False)
        tk.Label(self.log_panel, text="RUN THREAD", fg=BLUE2, bg=BG, font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=10, pady=(8, 4)
        )
        self.thread_text = tk.Text(
            self.log_panel,
            height=6,
            width=38,
            bg="#061729",
            fg=BLUE2,
            insertbackground=BLUE2,
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
        )
        self.thread_text.pack(anchor="w", padx=10, pady=(0, 10), fill="both", expand=True)
        self.thread_text.configure(state="disabled")

        timeline_frame = tk.Frame(lower, bg=BG)
        timeline_frame.pack(anchor="w", pady=(4, 0))
        self.timeline = ExecutionTimeline(timeline_frame, ("Consolas", 11, "bold"))

        self.status_line = tk.Label(shell, text="Run: waiting", fg=BLUE2, bg=BG, font=("Consolas", 10))
        self.status_line.pack(side="bottom", anchor="w", padx=20, pady=(6, 10))

        self.ladder_animator = StageLadderAnimator(
            self,
            PHASES,
            self._phase_dots,
            self.phase_labels,
            self.phase_reveals,
            self.phase_checks,
        )
        self.ladder_animator.reset()
        self.ladder_animator.tick()



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
        if hasattr(self, "artifact_link") and hasattr(self, "output_panel"):
            width = max(self.output_panel.winfo_width(), 520)
            self.artifact_link.configure(wraplength=max(420, width - 20))
        if hasattr(self, "agent_residue_label"):
            width = max(self.output_panel.winfo_width(), 520)
            self.agent_residue_label.configure(wraplength=max(420, width - 20))

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
        if self.run_complete and (not self.running):
            self.after(400, self._animate)
            return
        if self.running or self.has_activity:
            glow = "◉" if int(time.time() * 6) % 2 == 0 else "○"
            for p in PHASES:
                if not self.phase_truth[p]:
                    self._phase_dots[p].configure(text=glow)
        else:
            for p in PHASES:
                if not self.phase_truth[p]:
                    self._phase_dots[p].configure(text="○")

        if self.running:
            current = self.submit_lbl.cget("fg")
            self.submit_lbl.configure(fg=ORANGE2 if current == ORANGE else ORANGE)
        else:
            self.submit_lbl.configure(fg=ORANGE)

        self.status_indicator.tick(self.running)
        self.submit_btn.set_run_state(self.running, self.run_complete)
        self.submit_btn.tick(str(self.submit_btn.cget("state")) != "disabled")
        self.after(220, self._animate)

    def _lock(self, phase):
        if self.phase_truth.get(phase):
            return
        self.phase_truth[phase] = True
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
            self.status_indicator.set_status("IDLE", BLUE2)
            return

        events = read_events(self.run_path)
        if (not force) and (events == self.last_events):
            self._update_stream_box()
            self._update_cmd_box()
            return

        self.last_events = events
        self.has_activity = bool(events.strip())

        if "FROST_VERIFIED" in events:
            self._lock("Frost")
        if "GLACIER_VERIFIED" in events:
            self._lock("Glacier")
        if "CRYSTAL_VERIFIED" in events:
            self._lock("Crystal")
        if ("RESIDUE_LOCK" in events) or ("RESIDUE_EMPTY_LOCK" in events):
            self._lock("Residue")

        self._set_progress_from_events(events)
        self.ladder_animator.update_from_events(events)
        self.status_indicator.update(events, self.running)
        self.timeline.update(events)
        self.run_complete = "RUN_COMPLETE" in events
        self._update_thread_box(events)
        self._update_stream_box()
        self._update_cmd_box()

        ai_path = read_text(os.path.join(self.run_path, "ai_handoff_path.txt")).strip()
        self.status_line.configure(text=self._status_text_for_run(self.run_path))
        if "CRYSTAL_VERIFIED" in events and ai_path:
            if "RUN_COMPLETE" in events:
                self.artifact_link.configure(text=f"All that remains...\n{ai_path}")
            else:
                self.artifact_link.configure(text=ai_path)
        else:
            self.artifact_link.configure(text="All that remains...")

        if ("RUN_COMPLETE" in events) and (not self.running):
            if not self.handoff_visible:
                self.handoff_badge.pack(anchor="w", pady=(0, 8))
                self.handoff_visible = True
        else:
            if self.handoff_visible:
                self.handoff_badge.pack_forget()
                self.handoff_visible = False

        agentic_dir = os.path.join(self.run_path, "agentic")
        marker_ok = os.path.join(agentic_dir, "AGENTS_OK.json")
        marker_fail = os.path.join(agentic_dir, "AGENTS_FAIL.json")
        marker_active = os.path.join(agentic_dir, "AGENTS_ACTIVE.json")
        agent_state = None
        if os.path.exists(marker_fail):
            agent_state = "fail"
        elif os.path.exists(marker_ok):
            agent_state = "ok"
        elif os.path.exists(marker_active):
            agent_state = "active"

        if agent_state and (not self.agent_visible):
            self.agent_status_row.pack(anchor="w", pady=(2, 8))
            self.agent_visible = True
        elif (not agent_state) and self.agent_visible:
            self.agent_status_row.pack_forget()
            self.agent_visible = False
            self.agent_state = None

        if agent_state != self.agent_state:
            self.agent_state = agent_state
            if agent_state == "ok":
                self.agent_state_label.configure(text="AGENTS: OK", fg=BLUE2)
                self.agent_state_frame.configure(highlightbackground=BLUE2)
                self.agent_residue_label.configure(text="[ Agents OK — agentic/AGENTS_OK.json ]", fg=BLUE2)
                self.agent_residue_label.pack(anchor="w", pady=(0, 8))
            elif agent_state == "fail":
                self.agent_state_label.configure(text="AGENTS: FAILED", fg=ORANGE2)
                self.agent_state_frame.configure(highlightbackground=ORANGE2)
                self.agent_residue_label.configure(text="[ Agents FAILED — agentic/AGENTS_FAIL.json ]", fg=ORANGE2)
                self.agent_residue_label.pack(anchor="w", pady=(0, 8))
            elif agent_state == "active":
                self.agent_state_label.configure(text="AGENTS: RUNNING...", fg=BLUE2)
                self.agent_state_frame.configure(highlightbackground=BLUE2)
                self.agent_residue_label.pack_forget()
            else:
                self.agent_residue_label.pack_forget()

        agentic_dir = os.path.join(self.run_path, "agentic")
        marker_ok = os.path.join(agentic_dir, "AGENTS_OK.json")
        marker_fail = os.path.join(agentic_dir, "AGENTS_FAIL.json")
        marker_active = os.path.join(agentic_dir, "AGENTS_ACTIVE.json")
        agent_state = None
        if os.path.exists(marker_fail):
            agent_state = "fail"
        elif os.path.exists(marker_ok):
            agent_state = "ok"
        elif os.path.exists(marker_active):
            agent_state = "active"

        if agent_state and (not self.agent_visible):
            self.agent_status_row.pack(anchor="w", pady=(2, 8))
            self.agent_visible = True
        elif (not agent_state) and self.agent_visible:
            self.agent_status_row.pack_forget()
            self.agent_visible = False
            self.agent_state = None

        if agent_state != self.agent_state:
            self.agent_state = agent_state
            if agent_state == "ok":
                self.agent_state_label.configure(text="AGENTS: OK", fg=BLUE2)
                self.agent_state_frame.configure(highlightbackground=BLUE2)
                self.agent_residue_label.configure(text="[ Agents OK — agentic/AGENTS_OK.json ]", fg=BLUE2)
                self.agent_residue_label.pack(anchor="w", pady=(0, 8))
            elif agent_state == "fail":
                self.agent_state_label.configure(text="AGENTS: FAILED", fg=ORANGE2)
                self.agent_state_frame.configure(highlightbackground=ORANGE2)
                self.agent_residue_label.configure(text="[ Agents FAILED — agentic/AGENTS_FAIL.json ]", fg=ORANGE2)
                self.agent_residue_label.pack(anchor="w", pady=(0, 8))
            elif agent_state == "active":
                self.agent_state_label.configure(text="AGENTS: RUNNING...", fg=BLUE2)
                self.agent_state_frame.configure(highlightbackground=BLUE2)
                self.agent_residue_label.pack_forget()
            else:
                self.agent_residue_label.pack_forget()

    def _reset_phase_ladder(self):
        self.phase_truth = {p: False for p in PHASES}
        for p in PHASES:
            self.phase_labels[p].configure(fg=BLUE2)
            self._phase_dots[p].configure(text="○", fg=BLUE2)
            if hasattr(self, "phase_reveals") and p in self.phase_reveals:
                self.phase_reveals[p].configure(text="", fg=BLUE2)
            if hasattr(self, "phase_checks") and p in self.phase_checks:
                self.phase_checks[p].configure(text="", fg=BLUE2)
            if hasattr(self, "reveal_started"):
                self.reveal_started[p] = False
        if hasattr(self, "handoff_badge"):
            self.handoff_badge.pack_forget()
            self.handoff_visible = False
        if hasattr(self, "agent_frame"):
            self.agent_status_row.pack_forget()
            self.agent_visible = False
            self.agent_state = None
            self.agent_state_label.configure(text="AGENTS: NOT RUN", fg=BLUE2)
            self.agent_state_frame.configure(highlightbackground=BLUE2)
        if hasattr(self, "agent_residue_label"):
            self.agent_residue_label.pack_forget()
            self.agent_residue_state = None
        self._draw_progress(8)
        self.artifact_link.configure(text="All that remains...")
        self.timeline.reset()
        self._reset_thread_box()
        self._reset_stream_box()
        self._reset_cmd_box()
        self.run_complete = False
        self.has_activity = False
        self.ladder_animator.reset()

    def _update_thread_box(self, events: str):
        if not hasattr(self, "thread_text"):
            return
        lines = [line for line in events.splitlines() if line.strip()]
        tail = lines[-12:] if len(lines) > 12 else lines
        content = "\n".join(tail)
        if getattr(self, "_thread_cache", None) == content:
            return
        self._thread_cache = content
        self.thread_text.configure(state="normal")
        self.thread_text.delete("1.0", "end")
        self.thread_text.insert("end", content)
        self.thread_text.configure(state="disabled")

    def _reset_thread_box(self):
        if not hasattr(self, "thread_text"):
            return
        self.thread_text.configure(state="normal")
        self.thread_text.delete("1.0", "end")
        self.thread_text.configure(state="disabled")
        self._thread_cache = ""

    def _update_stream_box(self):
        if not hasattr(self, "stream_text") or (not self.run_path):
            return
        stream_path = os.path.join(self.run_path, "ui_cmd_stream.log")
        if not os.path.exists(stream_path):
            if getattr(self, "_stream_cache", None) != "":
                self._stream_cache = ""
                self.stream_text.configure(state="normal")
                self.stream_text.delete("1.0", "end")
                self.stream_text.configure(state="disabled")
            return
        content = read_text(stream_path)
        lines = [line for line in content.splitlines() if line.strip()]
        tail = lines[-10:] if len(lines) > 10 else lines
        display = "\n".join(tail)
        if getattr(self, "_stream_cache", None) == display:
            return
        self._stream_cache = display
        self.stream_text.configure(state="normal")
        self.stream_text.delete("1.0", "end")
        self.stream_text.insert("end", display)
        self.stream_text.configure(state="disabled")

    def _reset_stream_box(self):
        if not hasattr(self, "stream_text"):
            return
        self.stream_text.configure(state="normal")
        self.stream_text.delete("1.0", "end")
        self.stream_text.configure(state="disabled")
        self._stream_cache = ""

    def _update_cmd_box(self):
        if not hasattr(self, "cmd_text"):
            return
        cmd_path = os.path.join(self.run_path, "run_cmds.jsonl")
        if not os.path.exists(cmd_path):
            if getattr(self, "_cmd_cache", None) != "":
                self._cmd_cache = ""
                self.cmd_text.configure(state="normal")
                self.cmd_text.delete("1.0", "end")
                self.cmd_text.configure(state="disabled")
            return
        content = read_text(cmd_path)
        lines = [line for line in content.splitlines() if line.strip()]
        tail = lines[-10:] if len(lines) > 10 else lines
        display = "\n".join(tail)
        if getattr(self, "_cmd_cache", None) == display:
            return
        self._cmd_cache = display
        self.cmd_text.configure(state="normal")
        self.cmd_text.delete("1.0", "end")
        self.cmd_text.insert("end", display)
        self.cmd_text.configure(state="disabled")

    def _reset_cmd_box(self):
        if not hasattr(self, "cmd_text"):
            return
        self.cmd_text.configure(state="normal")
        self.cmd_text.delete("1.0", "end")
        self.cmd_text.configure(state="disabled")
        self._cmd_cache = ""

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

    def open_handoff_folder(self):
        if not self.run_path:
            messagebox.showinfo("ICE-CRAWLER", "No run folder yet.")
            return
        ai_path = read_text(os.path.join(self.run_path, "ai_handoff_path.txt")).strip()
        if ai_path and os.path.exists(ai_path):
            target = ai_path
        else:
            messagebox.showinfo("ICE-CRAWLER", "No handoff path yet.")
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
        self.stream_hook = CommandStreamHook(run_dir)
        self.last_events = ""
        self._reset_phase_ladder()

        def work():
            try:
                rc = run_orchestrator(repo_url, run_dir, stream_hook=self.stream_hook)
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
                    self.status_line.configure(text=f"Run error captured in UI stream. See traceback: {payload}")
                elif rc != 0:
                    self.status_line.configure(
                        text=f"Run failed (rc={rc}). Inspect CMD STREAM and ui_stdout.txt in: {payload}"
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
