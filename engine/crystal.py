# ❄ ICE-CRAWLER — CRYSTAL ENGINE (ROLE)
# Hash + manifest only.

import hashlib

def sha256_file(path: str):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()
