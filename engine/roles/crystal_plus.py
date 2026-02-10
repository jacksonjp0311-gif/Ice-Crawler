from __future__ import annotations
import os, json, traceback
from typing import Dict, Any, List

from engine.roles.crystal_engine import crystal_crystallize, CrystalConfig
from engine.agents.crystal_agents.agent_base import AgentContext, write_json, now_iso

# internal agents (separate files, main engine stays clean)
from engine.agents.crystal_agents import agent_filetype_stats
from engine.agents.crystal_agents import agent_imports_index
from engine.agents.crystal_agents import agent_hotspots
from engine.agents.crystal_agents import agent_readme_synthesis

AGENTS = [
    ("filetype_stats", agent_filetype_stats.run),
    ("imports_index", agent_imports_index.run),
    ("hotspots", agent_hotspots.run),
    ("readme_synthesis", agent_readme_synthesis.run),
]

def _ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def _write_text(path: str, text: str) -> None:
    _ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def crystal_plus(repo_root: str, run_state_dir: str, cfg: CrystalConfig | None = None) -> Dict[str, Any]:
    """
    Crystal++:
      1) Runs canonical crystal_engine.crystal_crystallize (unchanged)
      2) Runs internal agent suite to produce synthesis artifacts
      3) Writes AI_PACKET.md as a single “hand this to AI” entry point
    """
    cfg = cfg or CrystalConfig()

    # normalize dirs
    run_state_dir = run_state_dir.replace("\\", "/")
    _ensure_dir(run_state_dir)

    # where crystal_engine currently writes: run_state_dir/artifact/crystal/...
    synthesis_dir = os.path.join(run_state_dir, "artifact", "crystal", "synthesis")
    _ensure_dir(synthesis_dir)

    # --- Step 1: canonical crystal pass ---
    base_result = crystal_crystallize(repo_root, run_state_dir, cfg)

    # --- Step 2: internal agents pass ---
    ctx = AgentContext(
        repo_root=repo_root,
        run_state_dir=run_state_dir,
        synthesis_dir=synthesis_dir,
        max_files=getattr(cfg, "max_files", 600) if hasattr(cfg, "max_files") else 600,
        max_kb=getattr(cfg, "max_kb", 256.0) if hasattr(cfg, "max_kb") else 256.0,
    )

    agent_outputs: List[Dict[str, Any]] = []
    for name, fn in AGENTS:
        try:
            out_path = fn(ctx)
            agent_outputs.append({"agent": name, "ok": True, "path": out_path})
        except Exception as e:
            agent_outputs.append({
                "agent": name,
                "ok": False,
                "error": str(e),
                "trace": traceback.format_exc()[:4000],
            })

    # --- Step 3: assemble summary.json + AI_PACKET.md ---
    summary = {
        "ts": now_iso(),
        "repo_root": repo_root,
        "run_state_dir": run_state_dir,
        "synthesis_dir": synthesis_dir,
        "agents": agent_outputs,
        "note": "Crystal++ keeps crystal_engine.py untouched; synthesis is produced by internal agents.",
    }

    summary_path = os.path.join(synthesis_dir, "summary.json")
    write_json(summary_path, summary)

    # best-effort pointers (these exist in your current structure)
    ai_handoff_dir = os.path.join(run_state_dir, "ai_handoff")
    artifact_root = os.path.join(run_state_dir, "artifact")

    packet = []
    packet.append("# ICE-CRAWLER — AI PACKET (Crystal++)")
    packet.append("")
    packet.append("## What to hand the AI")
    packet.append("Give the AI THIS FILE plus the referenced JSONs. This is the single entrypoint.")
    packet.append("")
    packet.append("## Paths")
    packet.append(f"- Run root: {run_state_dir}")
    packet.append(f"- Artifact root: {artifact_root}")
    packet.append(f"- AI handoff dir: {ai_handoff_dir}")
    packet.append(f"- Synthesis dir: {synthesis_dir}")
    packet.append("")
    packet.append("## Load-bearing files (start here)")
    packet.append(f"- {os.path.join(synthesis_dir,'summary.json')}")
    packet.append(f"- {os.path.join(synthesis_dir,'filetype_stats.json')}")
    packet.append(f"- {os.path.join(synthesis_dir,'imports_index.json')}")
    packet.append(f"- {os.path.join(synthesis_dir,'hotspots.json')}")
    packet.append(f"- {os.path.join(synthesis_dir,'readme_synthesis.json')}")
    packet.append("")
    packet.append("## Crystal baseline artifacts (already produced by canonical crystal_engine)")
    packet.append(f"- {os.path.join(run_state_dir,'artifact','crystal','manifest_files.json')}")
    packet.append(f"- {os.path.join(run_state_dir,'artifact','crystal','manifest_hashes.json')}")
    packet.append(f"- {os.path.join(run_state_dir,'artifact_manifest.json')}")
    packet.append("")
    packet.append("## Ask the AI to do")
    packet.append("- Build an architecture map (modules → responsibilities → call graph hints).")
    packet.append("- Identify critical execution path: UI → orchestrator → frost/glacier/crystal → artifacts.")
    packet.append("- Propose next upgrades: deeper AST map, entrypoints, failure points, test harness.")
    packet.append("")
    packet_text = "\n".join(packet)

    ai_packet_path = os.path.join(synthesis_dir, "AI_PACKET.md")
    _write_text(ai_packet_path, packet_text)

    return {
        "base_result": base_result,
        "synthesis_summary": summary_path,
        "ai_packet": ai_packet_path,
        "agents": agent_outputs,
    }
