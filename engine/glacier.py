import json, os

ALLOW_EXT = (".py",".ps1",".c",".h",".md",".txt",".json",".yml",".yaml")

def glacier_select(paths, max_files: int):
    picked=[]
    for p in paths:
        if len(picked) >= max_files: break
        ll=p.lower().strip()
        if ll.endswith(ALLOW_EXT):
            picked.append(p.strip())
    return sorted(picked)

def glacier_emit(state_run: str, picked, repo_head: str):
    snap = os.path.join(state_run,"tree_snapshot.txt")
    with open(snap,"w",encoding="utf-8") as f:
        f.write("\n".join(picked))

    refp = os.path.join(state_run,"glacier_ref.json")
    with open(refp,"w",encoding="utf-8") as f:
        json.dump({"repo_head":repo_head,"picked_count":len(picked)}, f, indent=2)
