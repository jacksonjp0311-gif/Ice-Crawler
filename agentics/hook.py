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


def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


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
