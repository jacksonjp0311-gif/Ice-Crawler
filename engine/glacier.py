import os, json, subprocess

ALLOW_EXT = (".py", ".ps1", ".c", ".h", ".md", ".txt", ".json", ".yml", ".yaml")


def glacier_clone(repo_url: str, temp_dir: str):
    # EPHEMERAL MATERIALIZATION (shallow)
    subprocess.check_call(["git", "clone", "--depth=1", "--single-branch", repo_url, temp_dir])


def _triadic_bucket(path: str) -> str:
    """
    Triadic boundary-oriented projection buckets:
      - frost: source-like payloads
      - glacier: operational/config payloads
      - crystal: docs/meta payloads
    """
    p = path.lower()
    ext = os.path.splitext(p)[1]

    if ext in (".py", ".c", ".h"):
        return "frost"
    if ext in (".json", ".yml", ".yaml", ".ps1"):
        return "glacier"
    return "crystal"


def glacier_select(paths, max_files: int):
    allowed = []
    for p in paths:
        ll = p.lower().strip()
        if ll.endswith(ALLOW_EXT):
            allowed.append(p.strip())

    allowed = sorted(set(allowed))

    # Triadic balanced interleave keeps the projection diverse and deterministic.
    buckets = {"frost": [], "glacier": [], "crystal": []}
    for p in allowed:
        buckets[_triadic_bucket(p)].append(p)

    picked = []
    while len(picked) < max_files:
        progressed = False
        for key in ("frost", "glacier", "crystal"):
            if buckets[key] and len(picked) < max_files:
                picked.append(buckets[key].pop(0))
                progressed = True
        if not progressed:
            break

    return sorted(picked)


def glacier_emit(state_run: str, picked, repo_head: str):
    with open(os.path.join(state_run, "tree_snapshot.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(picked))
    with open(os.path.join(state_run, "glacier_ref.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "repo_head": repo_head,
                "picked_count": len(picked),
                "selection_mode": "triadic_balanced_v1",
            },
            f,
            indent=2,
        )
