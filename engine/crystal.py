import hashlib, json

def sha256_file(path: str):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_text(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def crystal_seal(state_run: str, manifest):
    # artifact hashes mirror (stable)
    with open(state_run+"/artifact_hashes.json","w",encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(state_run+"/crystal_report.md","w",encoding="utf-8") as f:
        f.write("# Crystal Seal\n\n")
        f.write(f"- Files: {len(manifest)}\n")
