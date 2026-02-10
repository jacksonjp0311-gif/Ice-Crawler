from __future__ import annotations
import os, re
from collections import defaultdict
from .agent_base import AgentContext, write_json, read_text, now_iso

IMPORT_RE = re.compile(r'^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\.]+))', re.M)

def run(ctx: AgentContext) -> str:
    imports = defaultdict(int)
    files_scanned = 0

    for root, _, files in os.walk(ctx.repo_root):
        if os.path.abspath(root).startswith(os.path.abspath(os.path.join(ctx.repo_root, "state"))):
            continue

        for fn in files:
            if not fn.lower().endswith(".py"):
                continue
            files_scanned += 1
            if files_scanned > ctx.max_files:
                break

            p = os.path.join(root, fn)
            # crude size gate
            try:
                if os.path.getsize(p) > int(ctx.max_kb * 1024):
                    continue
            except Exception:
                continue

            txt = read_text(p, max_bytes=int(ctx.max_kb * 1024))
            for m in IMPORT_RE.finditer(txt):
                mod = m.group(1) or m.group(2) or ""
                mod = mod.strip()
                if mod:
                    imports[mod] += 1

        if files_scanned > ctx.max_files:
            break

    top = sorted(imports.items(), key=lambda x: (-x[1], x[0]))[:500]
    out = {
        "agent": "imports_index",
        "ts": now_iso(),
        "repo_root": ctx.repo_root,
        "max_files": ctx.max_files,
        "max_kb": ctx.max_kb,
        "py_files_scanned": files_scanned,
        "top_imports": [{"module": k, "count": v} for k, v in top],
    }
    path = os.path.join(ctx.synthesis_dir, "imports_index.json")
    write_json(path, out)
    return path
