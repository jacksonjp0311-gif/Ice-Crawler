from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import os, json, time

@dataclass
class AgentContext:
    repo_root: str
    run_state_dir: str
    synthesis_dir: str
    max_files: int = 600
    max_kb: float = 256.0

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def write_json(path: str, data: Dict[str, Any]) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def read_text(path: str, max_bytes: int = 200_000) -> str:
    try:
        with open(path, "rb") as f:
            b = f.read(max_bytes)
        return b.decode("utf-8", errors="replace")
    except Exception:
        return ""

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")
