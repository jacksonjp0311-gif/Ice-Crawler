import json
import os
from typing import Optional

from .frost_fractal import run_frost_fractal
from .pipeline import run_pipeline


def _flag_disabled(env_key: str) -> bool:
    return os.environ.get(env_key, "").strip().lower() in {"1", "true", "yes", "on"}


def _agentics_enabled() -> bool:
    return not _flag_disabled("ICE_CRAWLER_AGENTIC_DISABLE")


def _frost_enabled() -> bool:
    return _agentics_enabled() and not _flag_disabled("ICE_CRAWLER_FROST_AGENTIC_DISABLE")


def _crystal_enabled() -> bool:
    return _agentics_enabled() and not _flag_disabled("ICE_CRAWLER_CRYSTAL_AGENTIC_DISABLE")


def frost_enabled() -> bool:
    return _frost_enabled()


def crystal_enabled() -> bool:
    return _crystal_enabled()


def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _agentic_dir(state_run: str) -> str:
    path = os.path.join(state_run, "agentic")
    os.makedirs(path, exist_ok=True)
    return path


def _write_marker(state_run: str, filename: str, payload: dict) -> str:
    path = os.path.join(_agentic_dir(state_run), filename)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return path


def _remove_marker(state_run: str, filename: str) -> None:
    path = os.path.join(_agentic_dir(state_run), filename)
    if os.path.exists(path):
        os.remove(path)


def mark_agents_running(state_run: str, stage: str) -> str:
    _remove_marker(state_run, "AGENTS_OK.json")
    _remove_marker(state_run, "AGENTS_FAIL.json")
    return _write_marker(state_run, "AGENTS_ACTIVE.json", {"stage": stage})


def mark_agents_ok(state_run: str, summary: dict) -> str:
    _remove_marker(state_run, "AGENTS_ACTIVE.json")
    return _write_marker(state_run, "AGENTS_OK.json", summary)


def mark_agents_fail(state_run: str, error: str) -> str:
    _remove_marker(state_run, "AGENTS_ACTIVE.json")
    return _write_marker(state_run, "AGENTS_FAIL.json", {"error": error})


def run_frost_hook(state_run: str, repo_url: str) -> Optional[dict]:
    if not _frost_enabled():
        return None
    max_weight = _env_float("ICE_CRAWLER_FROST_AGENTIC_MAX_WEIGHT", 80.0)
    return run_frost_fractal(repo_url, state_run, max_weight=max_weight)


def run_crystal_hook(state_run: str) -> Optional[dict]:
    if not _crystal_enabled():
        return None
    max_kb = _env_float("ICE_CRAWLER_AGENTIC_MAX_KB", 120.0)
    return run_pipeline(state_run, max_kb)
