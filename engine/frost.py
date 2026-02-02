# ❄ ICE-CRAWLER — FROST ENGINE (ROLE)
# Intake only: shallow clone into temp.

import subprocess

def frost_clone(repo_url: str, temp_dir: str):
    subprocess.check_call(["git","clone","--depth=1",repo_url,temp_dir])
