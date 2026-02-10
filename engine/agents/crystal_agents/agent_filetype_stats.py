from __future__ import annotations
import os
from collections import defaultdict
from .agent_base import AgentContext, write_json, now_iso

def run(ctx: AgentContext) -> str:
    counts = defaultdict(int)
    bytes_by_ext = defaultdict(int)
    scanned = 0

    for root, _, files in os.walk(ctx.repo_root):
        # skip our own run artifacts if repo_root == "."
        if os.path.abspath(root).startswith(os.path.abspath(os.path.join(ctx.repo_root, "state"))):
            continue

        for fn in files:
            scanned += 1
            if scanned > ctx.max_files:
                break
            p = os.path.join(root, fn)
            ext = os.path.splitext(fn)[1].lower() or "<noext>"
            try:
                sz = os.path.getsize(p)
            except Exception:
                sz = 0
            counts[ext] += 1
            bytes_by_ext[ext] += sz

        if scanned > ctx.max_files:
            break

    out = {
        "agent": "filetype_stats",
        "ts": now_iso(),
        "repo_root": ctx.repo_root,
        "max_files": ctx.max_files,
        "scanned_files": scanned,
        "counts": dict(sorted(counts.items(), key=lambda x: (-x[1], x[0]))),
        "bytes_by_ext": dict(sorted(bytes_by_ext.items(), key=lambda x: (-x[1], x[0]))),
    }
    path = os.path.join(ctx.synthesis_dir, "filetype_stats.json")
    write_json(path, out)
    return path
