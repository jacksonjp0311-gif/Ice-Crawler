import subprocess, datetime

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def frost_telemetry(repo_url: str):
    p = subprocess.run(["git","ls-remote",repo_url,"HEAD"],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    head="unknown"
    if p.returncode==0 and p.stdout.strip():
        head=p.stdout.strip().split()[0]
    return {"ts":utc_now(),"repo":repo_url,"head":head,"mode":"telemetry_only","clone_permitted":False}

def glacier_clone(repo_url: str, temp_dir: str):
    subprocess.check_call(["git","clone","--depth=1","--single-branch",repo_url,temp_dir])
