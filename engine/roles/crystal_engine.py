# ❄ ICE-CRAWLER — CRYSTAL ENGINE (FULL ANALYSIS + SYNTHESIS)
# Deterministic crystallization + accounting + synthesis bundle (no network calls)
#
# Output contract (relative to run_state_dir):
#   artifact/
#     crystal/
#       files/<repo-relative-path> (preserved directories)
#       manifest_files.json
#       manifest_hashes.json
#       crystal_copy_report.json
#       synthesis/
#         summary.json
#         hotspots.json
#         imports_index.json
#         filetype_stats.json
#         README_SYNTHESIS.txt
#
# This engine is intentionally offline + deterministic. Any “agentic” layer should
# attach AFTER these artifacts exist (do not mutate selection logic).

from __future__ import annotations
import os, json, hashlib, re
from dataclasses import dataclass
from typing import Dict, List, Tuple

TEXT_EXT = (".py",".ps1",".md",".txt",".json",".jsonl",".yml",".yaml",".ini",".cfg",".html",".css",".js",".ts",".tsx",".toml")

def _utc_now_iso() -> str:
    # Avoid importing datetime timezone complexity for determinism; caller may stamp elsewhere.
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _is_text_file(path: str) -> bool:
    low = path.lower()
    return low.endswith(TEXT_EXT)

def _safe_relpath(full_path: str, repo_root: str) -> str:
    rel = os.path.relpath(full_path, repo_root)
    rel = rel.replace("\\", "/")
    return rel

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def _write_json(path: str, obj) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def _read_text_bounded(path: str, max_bytes: int) -> str:
    with open(path, "rb") as f:
        raw = f.read(max_bytes)
    try:
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return raw.decode(errors="replace")

@dataclass(frozen=True)
class CrystalConfig:
    max_files: int = 600
    max_kb_per_file: int = 256
    max_total_kb: int = 30000
    include_ext: Tuple[str, ...] = TEXT_EXT

def crystal_select_files(repo_root: str, config: CrystalConfig) -> List[str]:
    # Deterministic walk: sort dirs/files
    picks: List[str] = []
    total_kb = 0.0

    for root, dirs, files in os.walk(repo_root):
        # Skip VCS + build artifacts deterministically
        dn = [d for d in dirs if d not in (".git","node_modules","dist","build","__pycache__")]
        dirs[:] = sorted(dn)

        for name in sorted(files):
            full = os.path.join(root, name)
            rel = _safe_relpath(full, repo_root)

            low = rel.lower()
            if low.startswith("state/runs/"):
                continue
            if low.startswith("dist/") or low.startswith("build/"):
                continue
            if low.endswith(".pyc"):
                continue

            if not low.endswith(config.include_ext):
                continue

            size_kb = os.path.getsize(full) / 1024.0
            if size_kb > float(config.max_kb_per_file):
                continue

            if len(picks) >= int(config.max_files):
                continue

            if (total_kb + size_kb) > float(config.max_total_kb):
                continue

            picks.append(rel)
            total_kb += size_kb

    return picks

def crystal_crystallize(repo_root: str, run_state_dir: str, config: CrystalConfig) -> Dict:
    artifact_root = os.path.join(run_state_dir, "artifact", "crystal")
    files_root = os.path.join(artifact_root, "files")
    synth_root = os.path.join(artifact_root, "synthesis")

    _ensure_dir(files_root)
    _ensure_dir(synth_root)

    selected = crystal_select_files(repo_root, config)

    copied: List[Dict] = []
    skipped: List[Dict] = []

    for rel in selected:
        src = os.path.join(repo_root, rel.replace("/", os.sep))
        if not os.path.exists(src):
            skipped.append({"path": rel, "reason": "missing"})
            continue

        dst = os.path.join(files_root, rel.replace("/", os.sep))
        _ensure_dir(os.path.dirname(dst))

        try:
            # copy bytes deterministically
            with open(src, "rb") as fsrc:
                data = fsrc.read()
            with open(dst, "wb") as fdst:
                fdst.write(data)

            h = hashlib.sha256(data).hexdigest()
            copied.append({"path": rel, "sha256": h, "bytes": len(data)})
        except Exception as e:
            skipped.append({"path": rel, "reason": f"copy_error:{type(e).__name__}"})

    # Manifests
    manifest_files = {"ts": _utc_now_iso(), "count": len(copied), "files": [c["path"] for c in copied]}
    manifest_hashes = {"ts": _utc_now_iso(), "count": len(copied), "hashes": [{"path": c["path"], "sha256": c["sha256"]} for c in copied]}
    report = {
        "ts": _utc_now_iso(),
        "selected": len(selected),
        "copied": len(copied),
        "skipped": skipped,
        "config": {
            "max_files": config.max_files,
            "max_kb_per_file": config.max_kb_per_file,
            "max_total_kb": config.max_total_kb,
            "include_ext": list(config.include_ext),
        },
        "artifact_root": "artifact/crystal",
        "files_root": "artifact/crystal/files",
    }

    _write_json(os.path.join(artifact_root, "manifest_files.json"), manifest_files)
    _write_json(os.path.join(artifact_root, "manifest_hashes.json"), manifest_hashes)
    _write_json(os.path.join(artifact_root, "crystal_copy_report.json"), report)

    # Synthesis (offline structural analysis)
    synthesis = synthesize_crystal_bundle(repo_root, files_root, copied, config)
    _write_json(os.path.join(synth_root, "summary.json"), synthesis["summary"])
    _write_json(os.path.join(synth_root, "hotspots.json"), synthesis["hotspots"])
    _write_json(os.path.join(synth_root, "imports_index.json"), synthesis["imports_index"])
    _write_json(os.path.join(synth_root, "filetype_stats.json"), synthesis["filetype_stats"])

    readme_path = os.path.join(synth_root, "README_SYNTHESIS.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("ICE-CRAWLER CRYSTAL — SYNTHESIS BUNDLE\n")
        f.write("This is a deterministic, offline structural analysis of the crystallized file set.\n\n")
        f.write(json.dumps(synthesis["summary"], indent=2, ensure_ascii=False))
        f.write("\n")

    return {
        "artifact_root": artifact_root,
        "copied": copied,
        "skipped": skipped,
        "summary": synthesis["summary"],
    }

def synthesize_crystal_bundle(repo_root: str, files_root: str, copied: List[Dict], config: CrystalConfig) -> Dict:
    # Basic but useful: filetype stats, import graph indices, hotspots (large/central)
    filetype_counts: Dict[str, int] = {}
    file_sizes: List[Tuple[str, int]] = []

    imports_index: Dict[str, List[str]] = {}
    reverse_imports: Dict[str, List[str]] = {}

    # Build a stable list
    copied_sorted = sorted(copied, key=lambda x: x["path"])

    for rec in copied_sorted:
        rel = rec["path"]
        ext = os.path.splitext(rel)[1].lower() or "(none)"
        filetype_counts[ext] = filetype_counts.get(ext, 0) + 1

        full = os.path.join(files_root, rel.replace("/", os.sep))
        try:
            b = os.path.getsize(full)
        except Exception:
            b = 0
        file_sizes.append((rel, b))

        # Imports: only parse Python
        if rel.lower().endswith(".py"):
            txt = _read_text_bounded(full, max_bytes=int(config.max_kb_per_file * 1024))
            imps = _extract_py_imports(txt)
            imports_index[rel] = sorted(imps)
            for m in imps:
                reverse_imports.setdefault(m, []).append(rel)

    # Hotspots: biggest files + most-importing files
    biggest = sorted(file_sizes, key=lambda x: x[1], reverse=True)[:25]
    import_counts = [(k, len(v)) for k, v in imports_index.items()]
    import_heavy = sorted(import_counts, key=lambda x: x[1], reverse=True)[:25]

    summary = {
        "ts": _utc_now_iso(),
        "repo_root": repo_root,
        "crystal_files": len(copied_sorted),
        "filetype_counts": filetype_counts,
        "largest_files": [{"path": p, "bytes": b} for p, b in biggest],
        "import_heavy": [{"path": p, "imports": c} for p, c in import_heavy],
        "notes": [
            "This synthesis is offline + deterministic.",
            "Use it to debug why Crystal is not emitting artifacts or why selection is too shallow.",
            "If you want deeper synthesis, increase max_files/max_total_kb cautiously."
        ],
    }

    hotspots = {
        "largest_files": [{"path": p, "bytes": b} for p, b in biggest],
        "most_imports": [{"path": p, "imports": c} for p, c in import_heavy],
        "reverse_imports_top": _top_reverse_imports(reverse_imports, k=25),
    }

    return {
        "summary": summary,
        "hotspots": hotspots,
        "imports_index": imports_index,
        "filetype_stats": filetype_counts,
    }

def _extract_py_imports(txt: str) -> List[str]:
    out = set()
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # import x, y as z
        m = re.match(r"^import\s+(.+)$", line)
        if m:
            chunk = m.group(1)
            parts = [p.strip() for p in chunk.split(",")]
            for p in parts:
                name = p.split(" as ")[0].strip()
                if name:
                    out.add(name)
            continue
        # from x import y
        m = re.match(r"^from\s+([A-Za-z0-9_\.]+)\s+import\s+", line)
        if m:
            out.add(m.group(1).strip())
            continue
    return sorted(out)

def _top_reverse_imports(reverse_imports: Dict[str, List[str]], k: int = 25) -> List[Dict]:
    items = []
    for mod, users in reverse_imports.items():
        items.append((mod, len(set(users))))
    items = sorted(items, key=lambda x: x[1], reverse=True)[:k]
    return [{"module": m, "used_by_files": c} for m, c in items]
