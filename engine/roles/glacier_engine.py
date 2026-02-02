# ❄ GLACIER ENGINE — bounded projection only
def glacier_pick(files,max_files):
    picked=[]
    for f in files:
        if len(picked)>=max_files: break
        picked.append(f)
    return picked
