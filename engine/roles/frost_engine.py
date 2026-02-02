# ❄ FROST ENGINE — clone intake only
import subprocess, os

def frost_clone(repo,temp):
    subprocess.check_call(["git","clone","--depth=1",repo,temp])
