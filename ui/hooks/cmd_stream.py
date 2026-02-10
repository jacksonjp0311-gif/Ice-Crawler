import os
import subprocess
from typing import Optional


class CommandStreamHook:
    """Streams orchestrator stdout into a run-local log for in-UI viewing."""

    def __init__(self, run_dir: str, stream_file: str = "ui_cmd_stream.log"):
        self.run_dir = run_dir
        self.stream_path = os.path.join(run_dir, stream_file)

    def reset(self):
        os.makedirs(self.run_dir, exist_ok=True)
        with open(self.stream_path, "w", encoding="utf-8"):
            pass

    def append_line(self, line: str):
        with open(self.stream_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def tail(self, max_lines: int = 12) -> str:
        if not os.path.exists(self.stream_path):
            return ""
        with open(self.stream_path, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f.readlines()]
        if len(lines) > max_lines:
            lines = lines[-max_lines:]
        return "\n".join(lines)

    def run_subprocess(
        self,
        cmd,
        cwd: Optional[str] = None,
        creationflags: int = 0,
        startupinfo=None,
    ):
        self.reset()
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=creationflags,
            startupinfo=startupinfo,
        )

        captured = []
        if proc.stdout is not None:
            for line in proc.stdout:
                line = line.rstrip("\n")
                captured.append(line)
                self.append_line(line)

        rc = proc.wait()
        full_output = "\n".join(captured)
        if full_output:
            full_output = full_output + "\n"
        return rc, full_output
