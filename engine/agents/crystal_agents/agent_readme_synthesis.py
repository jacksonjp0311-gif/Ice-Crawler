from __future__ import annotations
import os
from .agent_base import AgentContext, write_json, read_text, now_iso

def run(ctx: AgentContext) -> str:
    readme_paths = []
    for cand in ["README.md", "README.MD", "readme.md", "Readme.md"]:
        p = os.path.join(ctx.repo_root, cand)
        if os.path.exists(p):
            readme_paths.append(p)

    snippets = []
    for p in readme_paths[:3]:
        txt = read_text(p, max_bytes=80_000)
        snippets.append({
            "path": os.path.relpath(p, ctx.repo_root),
            "head": txt[:4000]
        })

    out = {
        "agent": "readme_synthesis",
        "ts": now_iso(),
        "repo_root": ctx.repo_root,
        "readmes_found": [os.path.relpath(p, ctx.repo_root) for p in readme_paths],
        "snippets": snippets,
        "note": "This is a lightweight extraction head for AI handoff; full synthesis is assembled by Crystal++ orchestrator.",
    }
    path = os.path.join(ctx.synthesis_dir, "readme_synthesis.json")
    write_json(path, out)
    return path
