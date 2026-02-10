from __future__ import annotations
import os
from .agent_base import AgentContext, write_json, now_iso

def run(ctx: AgentContext) -> str:
    rows = []
    files_scanned = 0

    for root, _, files in os.walk(ctx.repo_root):
        if os.path.abspath(root).startswith(os.path.abspath(os.path.join(ctx.repo_root, "state"))):
            continue

        for fn in files:
            files_scanned += 1
            if files_scanned > ctx.max_files:
                break
            p = os.path.join(root, fn)
            try:
                sz = os.path.getsize(p)
            except Exception:
                continue
            rows.append((sz, os.path.relpath(p, ctx.repo_root)))

        if files_scanned > ctx.max_files:
            break

    rows.sort(reverse=True, key=lambda x: x[0])
    top = rows[:100]

    out = {
        "agent": "hotspots",
        "ts": now_iso(),
        "repo_root": ctx.repo_root,
        "max_files": ctx.max_files,
        "files_scanned": files_scanned,
        "largest_files": [{"bytes": sz, "path": rp} for (sz, rp) in top],
    }
    path = os.path.join(ctx.synthesis_dir, "hotspots.json")
    write_json(path, out)
    return path
