import argparse
import datetime
import json
import os
from typing import Dict, List, Tuple

from .agent_manifest import AgentFile, AgentTask
from .phi_partition import GOLDEN_RATIO, phi_partition


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def _artifact_path(state_run: str, rel_path: str) -> str:
    return os.path.join(state_run, "artifact", rel_path.replace("/", "_"))


def _load_manifest(state_run: str) -> List[Dict]:
    manifest_path = os.path.join(state_run, "artifact_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _build_items(state_run: str, manifest: List[Dict]) -> List[Dict]:
    items = []
    for entry in manifest:
        rel_path = entry["path"]
        artifact_path = _artifact_path(state_run, rel_path)
        if not os.path.exists(artifact_path):
            continue
        size_kb = os.path.getsize(artifact_path) / 1024.0
        items.append(
            {
                "path": rel_path,
                "sha256": entry.get("sha256", ""),
                "size_kb": round(size_kb, 3),
            }
        )
    return items


def _partition_items(
    items: List[Dict],
    max_kb: float,
) -> Tuple[List[AgentTask], List[Dict]]:
    partitions, oversize = phi_partition(items, size_key="size_kb", max_size=max_kb)
    tasks: List[AgentTask] = []
    for idx, partition in enumerate(partitions, start=1):
        files = [
            AgentFile(path=item["path"], sha256=item["sha256"], size_kb=item["size_kb"])
            for item in partition.items
        ]
        total_kb = round(partition.total_size, 3)
        tasks.append(
            AgentTask(
                agent_id=f"phi_agent_{idx:02d}",
                depth=partition.depth,
                coherence_weight=round(GOLDEN_RATIO ** (-partition.depth), 6),
                total_kb=total_kb,
                files=files,
            )
        )
    return tasks, oversize


def _summarize(tasks: List[AgentTask], oversize: List[Dict], total_files: int) -> Dict:
    partitions = len(tasks)
    fragmentation_pressure = round(partitions / max(1, total_files), 4)
    coordination_coherence = round(1.0 - min(0.95, fragmentation_pressure), 4)
    return {
        "partition_count": partitions,
        "total_files": total_files,
        "oversize_files": len(oversize),
        "fragmentation_pressure": fragmentation_pressure,
        "coordination_coherence": coordination_coherence,
    }


def _write_outputs(state_run: str, max_kb: float, tasks: List[AgentTask], oversize: List[Dict]) -> None:
    out_dir = os.path.join(state_run, "agentic")
    os.makedirs(out_dir, exist_ok=True)

    task_payloads = [task.to_dict() for task in tasks]

    with open(os.path.join(out_dir, "agent_tasks.json"), "w", encoding="utf-8") as handle:
        json.dump(task_payloads, handle, indent=2)

    summary = _summarize(tasks, oversize, sum(len(task.files) for task in tasks) + len(oversize))

    agent_index = {
        "ts": utc_now(),
        "phi": GOLDEN_RATIO,
        "max_kb": max_kb,
        "summary": summary,
    }

    if oversize:
        agent_index["oversize"] = oversize

    with open(os.path.join(out_dir, "agent_index.json"), "w", encoding="utf-8") as handle:
        json.dump(agent_index, handle, indent=2)

    with open(os.path.join(out_dir, "agent_prompt.md"), "w", encoding="utf-8") as handle:
        handle.write("# ICE-CRAWLER Φ-Agentic Task Prompt\n\n")
        handle.write("You are an extraction agent operating on a bounded partition.\n\n")
        handle.write("Rules:\n")
        handle.write("- Only read the files listed for your agent_id.\n")
        handle.write("- Preserve deterministic summaries; do not fabricate missing context.\n")
        handle.write("- Report risks, invariants, and cross-links needed for synthesis.\n\n")
        handle.write("Deliverables:\n")
        handle.write("- Summary of assigned files.\n")
        handle.write("- Invariants or shared dependencies.\n")
        handle.write("- Suggested merge/synthesis notes.\n")


def run_pipeline(state_run: str, max_kb: float) -> Dict:
    manifest = _load_manifest(state_run)
    items = _build_items(state_run, manifest)
    tasks, oversize = _partition_items(items, max_kb)
    _write_outputs(state_run, max_kb, tasks, oversize)
    return {
        "state_run": state_run,
        "task_count": len(tasks),
        "oversize": len(oversize),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Φ-extremal agentic partitioning.")
    parser.add_argument("state_run", help="Path to a completed ICE-CRAWLER run directory")
    parser.add_argument("--max-kb", type=float, default=120.0, help="Max size per partition in KB")
    args = parser.parse_args()

    result = run_pipeline(args.state_run, args.max_kb)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
