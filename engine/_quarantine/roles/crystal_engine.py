# ❄ CRYSTAL ENGINE — manifest + hashes only
import hashlib, json

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        h.update(f.read())
    return h.hexdigest()
