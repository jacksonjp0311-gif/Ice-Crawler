import hashlib, json

def sha256_file(path:str):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):
            h.update(c)
    return h.hexdigest()

def sha256_text(s:str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def crystal_seal(state_run,manifest):
    json.dump(manifest,open(state_run+"/artifact_hashes.json","w",encoding="utf-8"),indent=2)
    open(state_run+"/crystal_report.md","w",encoding="utf-8").write("# Crystal Seal\n")
