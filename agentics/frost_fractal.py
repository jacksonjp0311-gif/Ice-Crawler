import datetime
import json
import os
import subprocess
import sys
from typing import Dict, List, Tuple

from .phi_partition import GOLDEN_RATIO, phi_partition


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def _run(cmd: List[str]) -> Tuple[int, str]:
    creationflags = 0
    startupinfo = None
    if sys.platform.startswith("win"):
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
        startupinfo=startupinfo,
    )
    return proc.returncode, proc.stdout


def _write_cmd(state_run: str, cmd: List[str], note: str) -> None:
    path = os.path.join(state_run, "run_cmds.jsonl")
    rec = {"ts": utc_now(), "cmd": cmd, "note": note}
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _parse_refs(output: str) -> List[Dict]:
    refs = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        sha, ref = parts[0], parts[1]
        weight = max(1.0, float(len(ref)))
        refs.append({"ref": ref, "sha": sha, "weight": weight})
    return refs


def _prefix_counts(refs: List[Dict]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for ref in refs:
        parts = ref["ref"].split("/")
        prefix = "/".join(parts[:3]) if len(parts) >= 3 else ref["ref"]
        counts[prefix] = counts.get(prefix, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _write_outputs(state_run: str, max_weight: float, tasks: List[Dict], oversize: List[Dict], refs: List[Dict]) -> None:
    out_dir = os.path.join(state_run, "frost_agentic")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "frost_agent_tasks.json"), "w", encoding="utf-8") as handle:
        json.dump(tasks, handle, indent=2)

    index = {
        "ts": utc_now(),
        "phi": GOLDEN_RATIO,
        "max_weight": max_weight,
        "ref_count": len(refs),
        "task_count": len(tasks),
        "oversize_refs": len(oversize),
        "prefix_counts": _prefix_counts(refs),
    }
    if oversize:
        index["oversize"] = oversize

    with open(os.path.join(out_dir, "frost_agent_index.json"), "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2)

    with open(os.path.join(out_dir, "frost_agent_prompt.md"), "w", encoding="utf-8") as handle:
        handle.write("# ICE-CRAWLER Φ-Frost Agent Prompt\n\n")
        handle.write("You are operating in the Frost telemetry boundary (no clone).\n\n")
        handle.write("Rules:\n")
        handle.write("- Only analyze the refs listed for your agent_id.\n")
        handle.write("- Do not perform repository cloning.\n")
        handle.write("- Surface branch/tag naming signals, release patterns, and hot zones.\n\n")
        handle.write("Deliverables:\n")
        handle.write("- Ref summary and inferred hotspots.\n")
        handle.write("- Suggested areas for Glacier focus.\n")
        handle.write("- Any anomalies in ref topology.\n")

    with open(os.path.join(out_dir, "glacier_hints.json"), "w", encoding="utf-8") as handle:
        json.dump({"prefix_counts": _prefix_counts(refs)}, handle, indent=2)

    with open(os.path.join(out_dir, "frost_report.md"), "w", encoding="utf-8") as handle:
        handle.write("# ICE-CRAWLER Φ-Frost Report\n\n")
        handle.write(f"Timestamp: {utc_now()}\n\n")
        handle.write("## Summary\n")
        handle.write(f"- Ref count: {len(refs)}\n")
        handle.write(f"- Task count: {len(tasks)}\n")
        handle.write(f"- Oversize refs: {len(oversize)}\n\n")
        handle.write("## Top ref prefixes\n")
        for prefix, count in _prefix_counts(refs).items():
            handle.write(f"- {prefix}: {count}\n")
        handle.write("\n## Glacier hints\n")
        handle.write("- Use prefix density to bias Glacier selection toward active branches/tags.\n")


def run_frost_fractal(repo_url: str, state_run: str, max_weight: float = 80.0, max_refs: int = 2000) -> Dict:
    _write_cmd(state_run, ["git", "ls-remote", "--heads", "--tags", repo_url], "agentic_frost_refs")
    rc, out = _run(["git", "ls-remote", "--heads", "--tags", repo_url])
    refs = _parse_refs(out) if rc == 0 else []
    refs = refs[:max_refs]

    partitions, oversize = phi_partition(refs, size_key="weight", max_size=max_weight, sort_key="ref")
    tasks: List[Dict] = []
    for idx, partition in enumerate(partitions, start=1):
        total_weight = round(partition.total_size, 3)
        tasks.append(
            {
                "agent_id": f"frost_phi_agent_{idx:02d}",
                "depth": partition.depth,
                "coherence_weight": round(GOLDEN_RATIO ** (-partition.depth), 6),
                "total_weight": total_weight,
                "refs": partition.items,
            }
        )

    _write_outputs(state_run, max_weight, tasks, oversize, refs)
    return {"state_run": state_run, "task_count": len(tasks), "oversize": len(oversize)}
