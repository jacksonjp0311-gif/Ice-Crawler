import json, os
ALLOW_EXT=(".py",".ps1",".c",".h",".md",".txt",".json",".yml",".yaml")

def glacier_select(paths,max_files:int):
    picked=[]
    for p in paths:
        if len(picked)>=max_files: break
        if p.lower().endswith(ALLOW_EXT):
            picked.append(p.strip())
    return sorted(picked)

def glacier_emit(state_run,picked,repo_head):
    open(os.path.join(state_run,"tree_snapshot.txt"),"w",encoding="utf-8").write("\n".join(picked))
    json.dump({"repo_head":repo_head,"picked_count":len(picked)},
              open(os.path.join(state_run,"glacier_ref.json"),"w",encoding="utf-8"),indent=2)
