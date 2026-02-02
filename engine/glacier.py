# ❄ ICE-CRAWLER — GLACIER ENGINE (ROLE)
# Bounded projection: filter + cap.

ALLOW_EXT = (".py",".ps1",".c",".h",".md",".txt",".json",".yml",".yaml")

def glacier_select(paths, max_files: int):
    picked=[]
    for p in paths:
        if len(picked) >= max_files:
            break
        ll=p.lower().strip()
        if not ll:
            continue
        if ll.endswith(ALLOW_EXT):
            picked.append(p.strip())
    return picked
