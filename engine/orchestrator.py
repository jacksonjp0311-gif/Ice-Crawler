import os, sys, json, shutil, subprocess, datetime, time, stat, importlib.util, importlib

from .frost import frost_telemetry
from .glacier import glacier_clone, glacier_select, glacier_emit
print("========== ICE-CRAWLER DEBUG ==========")
print("Orchestrator starting")
print("Python path OK")
print("Loading crystal engine…")
print("===== CRYSTAL DEBUG =====")
print("Orchestrator running")
from .crystal import sha256_file, sha256_text, crystal_seal

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def run(cmd, cwd=None):
    p=subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout

def _on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def purge_dir_strict(path, tries=40, sleep_s=0.25):
    try:
        if os.path.exists(path):
            run(["git","-C",path,"clean","-fdx"])
    except Exception:
        pass
    for _ in range(tries):
        if os.path.exists(path):
            try:
                shutil.rmtree(path, ignore_errors=False, onerror=_on_rm_error)
            except Exception:
                pass
        if not os.path.exists(path):
            return True
        time.sleep(sleep_s)
    return (not os.path.exists(path))

def emit_ui(state_run: str, event: str, payload=None):
    p = os.path.join(state_run,"ui_events.jsonl")
    rec = {"ts":utc_now(),"event":event}
    if payload is not None:
        rec["payload"]=payload
    with open(p,"a",encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False)+"\n")

def emit_cmd(state_run: str, cmd, note=None):
    p = os.path.join(state_run, "run_cmds.jsonl")
    rec = {"ts": utc_now(), "cmd": cmd}
    if note:
        rec["note"] = note
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

def agentics_hook():
    if importlib.util.find_spec("agentics.hook") is None:
        return None
    return importlib.import_module("agentics.hook")

def ai_handoff_emit(state_run: str, manifest, repo_url: str, repo_head: str):
    ai_dir = os.path.join(state_run, "ai_handoff")
    ensure_dir(ai_dir)

    compact = {
        "ts": utc_now(),
        "repo": repo_url,
        "repo_head": repo_head,
        "file_count": len(manifest),
        "files": [{"path":m["path"], "sha256":m["sha256"]} for m in manifest[:50]]
    }

    manifest_compact = os.path.join(ai_dir, "manifest_compact.json")
    with open(manifest_compact,"w",encoding="utf-8") as f:
        json.dump(compact, f, indent=2)

    # Root seal binds: head + manifest_compact hash
    mc_hash = sha256_file(manifest_compact)
    root_seal = sha256_text(f"{repo_head}|{mc_hash}|ICE_CRAWLER_V4_0P")

    with open(os.path.join(ai_dir,"root_seal.txt"),"w",encoding="utf-8") as f:
        f.write(root_seal + "\n")
        f.write(f"repo_head={repo_head}\n")
        f.write(f"manifest_compact_sha256={mc_hash}\n")

    prompt_ready = os.path.join(ai_dir, "PROMPT_READY.md")
    with open(prompt_ready,"w",encoding="utf-8") as f:
        f.write("# ICE-CRAWLER AI HANDOFF (PROMPT READY)\n\n")
        f.write("You are given a sealed, bounded repo fossil.\n\n")
        f.write("Rules:\n")
        f.write("- Treat the bundle as read-only input.\n")
        f.write("- Use manifest_compact.json + root_seal.txt as integrity anchors.\n")
        f.write("- Do NOT assume missing files exist.\n\n")
        f.write("Deliver:\n")
        f.write("- A concise technical summary.\n")
        f.write("- Risks / sensitive areas.\n")
        f.write("- Suggested next actions.\n")

    # Proof token for UI
    with open(os.path.join(state_run,"ai_handoff_path.txt"),"w",encoding="utf-8") as f:
        f.write(ai_dir)

    emit_ui(state_run, "AI_HANDOFF_READY", {"ai_handoff": ai_dir, "root_seal": root_seal})


# ===== AUTO_ARGS_PATCH =====
import sys
if len(sys.argv) < 6:
    print("[PATCH] Injecting default orchestrator args")
    sys.argv = [
        sys.argv[0],
        ".",                    # repo
        "state/runs/test_run",  # state_run
        "600",                  # max_files
        "256",                  # max_kb
        "state/tmp"             # temp_dir
    ]
# ===========================

def main():
    repo      = sys.argv[1]
    state_run = sys.argv[2]
    max_files = int(sys.argv[3])
    max_kb    = float(sys.argv[4])
    temp_dir  = sys.argv[5]

    ensure_dir(state_run)
    residue_path = os.path.join(state_run,"residue_truth.json")

    emit_ui(state_run, "RUN_BEGIN", {"repo": repo})
    agentic = agentics_hook()
    agentic_ran = False

    # Frost: telemetry-only
    emit_ui(state_run, "FROST_PENDING")
    emit_cmd(state_run, ["git", "ls-remote", repo, "HEAD"], note="frost_telemetry")
    frost = frost_telemetry(repo)
    with open(os.path.join(state_run,"frost_summary.json"),"w",encoding="utf-8") as f:
        json.dump(frost, f, indent=2)
    emit_ui(state_run, "FROST_VERIFIED", {"head": frost.get("head","unknown")})
    emit_ui(state_run, "UI_EVENT:FROST_PENDING_TO_VERIFIED")

    try:
        if os.path.exists(temp_dir):
            purge_dir_strict(temp_dir)

        if agentic is not None and agentic.frost_enabled():
            try:
                agentic.mark_agents_running(state_run, "frost")
                frost_result = agentic.run_frost_hook(state_run, repo)
                if frost_result is not None:
                    agentic_ran = True
                emit_ui(state_run, "AGENTIC_FROST_VERIFIED")
            except Exception as exc:
                agentic.mark_agents_fail(state_run, str(exc))
                emit_ui(state_run, "AGENTIC_FROST_ERROR", {"error": str(exc)})
        elif agentic is not None and agentic_ran and (not agentic.crystal_enabled()):
            agentic.mark_agents_ok(state_run, {"stage": "frost"})

        # Glacier: ephemeral clone + bounded selection
        emit_ui(state_run, "GLACIER_PENDING")
        emit_ui(state_run, "UI_EVENT:GLACIER_PENDING")
        emit_cmd(state_run, ["git", "clone", "--depth=1", "--single-branch", repo, temp_dir], note="glacier_clone")
        glacier_clone(repo, temp_dir)

        emit_cmd(state_run, ["git", "-C", temp_dir, "ls-files"], note="glacier_ls_files")
        rc, out = run(["git","-C",temp_dir,"ls-files"])
        picked = glacier_select(out.splitlines(), max_files)
        glacier_emit(state_run, picked, frost.get("head","unknown"))
        emit_ui(state_run, "GLACIER_VERIFIED", {"picked": len(picked)})
        emit_ui(state_run, "UI_EVENT:GLACIER_VERIFIED")

        # Crystal: deterministic bundle
        emit_ui(state_run, "CRYSTAL_PENDING")
        emit_ui(state_run, "UI_EVENT:CRYSTAL_PENDING")
        bundle = os.path.join(state_run, "artifact")
        ensure_dir(bundle)

        manifest=[]
        skipped_missing=[]
        skipped_oversize=[]
        for rel in picked:
            src=os.path.join(temp_dir, rel)
            if not os.path.exists(src):
                skipped_missing.append(rel)
                continue

            size_kb = os.path.getsize(src)/1024.0
            if size_kb > max_kb:
                skipped_oversize.append({"path": rel, "size_kb": round(size_kb, 3)})
                continue

            # Preserve repository-relative paths inside a single artifact root.
            # This avoids filename collisions that can occur with flattening
            # (for example: "a/b_c.py" vs "a_b/c.py").
            dst=os.path.join(bundle, rel)
            ensure_dir(os.path.dirname(dst))
            shutil.copy2(src, dst)

            manifest.append({"path":rel,"artifact_rel":rel,"sha256":sha256_file(dst)})

        manifest = sorted(manifest, key=lambda x: x["path"])
        skipped_missing = sorted(set(skipped_missing))
        skipped_oversize = sorted(skipped_oversize, key=lambda x: x["path"])

        with open(os.path.join(state_run,"artifact_manifest.json"),"w",encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        with open(os.path.join(state_run,"crystal_index.json"),"w",encoding="utf-8") as f:
            json.dump({"ts":utc_now(),"count":len(manifest)}, f, indent=2)

        with open(os.path.join(state_run, "crystal_copy_report.json"), "w", encoding="utf-8") as f:
            json.dump(
                {
                    "ts": utc_now(),
                    "picked_count": len(picked),
                    "crystallized_count": len(manifest),
                    "skipped_missing": skipped_missing,
                    "skipped_oversize": skipped_oversize,
                },
                f,
                indent=2,
            )

        crystal_seal(repo, state_run)

        # UI contract (extended)
        with open(os.path.join(state_run,"ui_contract.json"),"w",encoding="utf-8") as f:
            json.dump({
                "ui_reads_only":[
                    "artifact_manifest.json",
                    "artifact_hashes.json",
                    "crystal_index.json",
                    "crystal_copy_report.json",
                    "ui_events.jsonl",
                    "ai_handoff_path.txt"
                ],
                "ui_never_runs_git": True
            }, f, indent=2)

        emit_ui(state_run, "CRYSTAL_VERIFIED", {"count": len(manifest)})
        emit_ui(state_run, "UI_EVENT:CRYSTAL_VERIFIED")

        # AI handoff (restored)
        ai_handoff_emit(state_run, manifest, repo, frost.get("head","unknown"))

        if agentic is not None and agentic.crystal_enabled():
            try:
                agentic.mark_agents_running(state_run, "crystal")
                crystal_result = agentic.run_crystal_hook(state_run)
                if crystal_result is not None:
                    agentic_ran = True
                emit_ui(state_run, "AGENTIC_CRYSTAL_VERIFIED")
            except Exception as exc:
                agentic.mark_agents_fail(state_run, str(exc))
                emit_ui(state_run, "AGENTIC_CRYSTAL_ERROR", {"error": str(exc)})
            else:
                if agentic_ran:
                    agentic.mark_agents_ok(state_run, {"stage": "crystal"})
        elif agentic is not None and agentic_ran:
            agentic.mark_agents_ok(state_run, {"stage": "frost"})

    finally:
        purge_ok = purge_dir_strict(temp_dir)
        rho = "empty" if (not os.path.exists(temp_dir)) else "violation"
        with open(residue_path,"w",encoding="utf-8") as f:
            json.dump({"ts":utc_now(),"rho_post":rho,"purge_ok":purge_ok}, f, indent=2)

    if os.path.exists(temp_dir):
        raise RuntimeError("Residue violation")

    emit_ui(state_run, "RESIDUE_EMPTY_LOCK")
    emit_ui(state_run, "UI_EVENT:RESIDUE_EMPTY_LOCK")
    emit_ui(state_run, "RUN_COMPLETE")
    return 0

if __name__=="__main__":
    raise SystemExit(main())






