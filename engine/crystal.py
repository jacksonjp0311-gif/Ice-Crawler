from engine.roles.crystal_engine import (
    sha256_file,
    crystal_crystallize,
    CrystalConfig
)

import hashlib, os

def sha256_text(text:str)->str:
    if isinstance(text,str):
        text = text.encode("utf-8",errors="ignore")
    return hashlib.sha256(text).hexdigest()

def crystal_seal(repo_root=".", run_state_dir="state/runs/latest"):
    print("[CRYSTAL] starting analysis")
    os.makedirs(run_state_dir, exist_ok=True)
    cfg = CrystalConfig()
    result = crystal_crystallize(repo_root, run_state_dir, cfg)
    print("[CRYSTAL] done")
    return result
