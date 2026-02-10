# ICE-CRAWLER

Triadic zero-trace repository ingestion for analysis workflows.

ICE-CRAWLER ingests an untrusted repository through three isolated engines—**Frost → Glacier → Crystal**—then emits a deterministic artifact set and teardown proof for auditability.

## Overview

ICE-CRAWLER is designed for **containment-first** repository analysis:

- **Frost (telemetry):** resolves repository metadata (for example HEAD) without cloning.
- **Glacier (ephemeral materialization):** performs a shallow clone into temporary workspace and deterministic triadic-balanced bounded file selection.
- **Crystal (deterministic crystallization):** generates read-only analysis artifacts and hash manifests.
- **Residue lock:** teardown is enforced and recorded as a final completion event.

The UI is an observational truth surface. It reads run fossils (event logs + artifact pointers) and never performs git operations itself.

## What this project is

- A practical scaffold for bounded, deterministic repo ingestion.
- A zero-trace oriented workflow where temporary workspace is deleted after run completion.
- A UI ladder that reflects engine-emitted truth events in near real time.

## What this project is not

- Not a malware detector or complete security product.
- Not a universal safety guarantee against adversarial repos.
- Not a fourth ingestion phase (the UI remains observational only).

## Architecture at a glance

```text
Repo URL
  │
  ├─ Frost   → frost_summary.json
  ├─ Glacier → glacier_ref.json + tree_snapshot.txt
  ├─ Crystal → artifact/, artifact_manifest.json, artifact_hashes.json
  └─ Residue → residue_truth.json + RESIDUE_EMPTY_LOCK event
```

Core orchestration entrypoint:

- `engine/orchestrator.py`

UI entrypoint:

- `ui/ice_ui.py`

Recent enhancement: Glacier now uses a deterministic **triadic-balanced selector** (frost/glacier/crystal buckets) to keep artifact projection diverse and bounded while preserving deterministic ordering.

Optional extension: Φ-extremal agentic hooks can partition Frost refs and Crystal artifacts into bounded agent tasks for multi-agent extraction (opt-out via environment flags).

## Repository layout

- `engine/` — phase engines and orchestrator.
- `ui/` — Tkinter UI and UI registry metadata.
- `state/runs/<run_...>/` — per-run fossils and artifacts.
- `artifact/` — project-level artifact bundle metadata.


## Root folder mini map

Quick directory guide for top-level project folders:

- `engine/`
  - **Engine role:** Core run pipeline (Frost telemetry, Glacier selection, Crystal crystallization, residue lock).
  - **How it works:** `engine/orchestrator.py` executes stages in order, emits `ui_events.jsonl`, and writes run artifacts into `state/runs/<run>/`.
  - **Mini directory:** `frost.py`, `glacier.py`, `crystal.py`, `orchestrator.py` (+ `_quarantine/` experiments).

- `ui/`
  - **Engine role:** Observational UI surface only.
  - **How it works:** Reads run fossils (`ui_events.jsonl`, manifests, handoff pointers), renders ladder state, never executes git.
  - **Mini directory:** `ice_ui.py`, `animations/`, `design/`, `assets/`, `engine_registry.json`.

- `agentics/`
  - **Engine role:** Optional hook layer for task partitioning around Frost and Crystal outputs.
  - **How it works:** Activated by environment flags; reads run outputs and emits bounded agent task bundles in run folders.
  - **Mini directory:** `hook.py`, `pipeline.py`, `phi_partition.py`, `agent_manifest.py`, `frost_fractal.py`.

- `docs/`
  - **Engine role:** Architecture and formal constraints.
  - **How it works:** Captures invariants and design intent for triadic ingestion and optional agentic overlays.
  - **Mini directory:** `ICE_CRAWLER_ARCHITECTURE_v1_1.md`, `CODEX_777_...md`, `CODEX_PHI_...md`.

- `scripts/`
  - **Engine role:** Launcher/build convenience wrappers.
  - **How it works:** Shell/PowerShell wrappers for UI launch and packaging workflows.
  - **Mini directory:** `launchers/`, `build/`.

- `ledger/`
  - **Engine role:** Historical run-event append log.
  - **How it works:** Records selected run checkpoints and completion facts.
  - **Mini directory:** `ice_crawler_ledger.jsonl`.

- `artifact/`
  - **Engine role:** Project-level static artifact bundle metadata (not per-run output).
  - **How it works:** Stores baseline bundle manifest references under source control.
  - **Mini directory:** `bundles/artifact_manifest.json`.

## Requirements

- Python 3.10+
- Git CLI available on PATH
- Network access for remote repository telemetry/clone

## Clone this repository

### Bash (Linux/macOS)

```bash
git clone https://github.com/<your-org>/Ice-Crawler.git
cd Ice-Crawler
```

### PowerShell (Windows)

```powershell
git clone https://github.com/<your-org>/Ice-Crawler.git
Set-Location .\Ice-Crawler
```

## Launch from repository root (single canonical entrypoint)

### Single entrypoint (all platforms)

Use exactly one launcher: **`icecrawler.py`** at the repository root.

```bash
python icecrawler.py
```

```powershell
python .\icecrawler.py
```

Behavior:

- Runs the UI through your current Python interpreter (default/recommended).
- Optional EXE mode only when explicitly requested: `python icecrawler.py --prefer-exe` (Windows).

### Building a Windows EXE locally (optional)

To ensure compatibility with your machine (and avoid DLL/runtime mismatch), build locally:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build\build_windows_exe.ps1
```

This outputs `dist\IceCrawler.exe`.

### Snowflake app icon

The UI now attempts to load an app icon from:

- `ui/assets/snowflake.ico` (Windows preferred)
- `ui/assets/snowflake.png` (fallback)

If you place either file there, the window icon will update automatically.

## Running the UI

### Bash (Linux/macOS)

```bash
python icecrawler.py
```

Then paste a repository URL and click the glowing triangle **PRESS TO SUBMIT TO ICE CRAWLER** control.

### PowerShell (Windows)

```powershell
python .\icecrawler.py
```

Then paste a repository URL and click the glowing triangle **PRESS TO SUBMIT TO ICE CRAWLER** control.

## Running orchestrator directly (CLI)

### Bash

```bash
RUN_DIR="state/runs/run_$(date +%Y%m%d_%H%M%S)"
TEMP_DIR="state/_temp_repo"
mkdir -p "$RUN_DIR"
python -m engine.orchestrator "https://github.com/<org>/<repo>.git" "$RUN_DIR" 50 120 "$TEMP_DIR"
```

### PowerShell

```powershell
$runDir = "state/runs/run_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$tempDir = "state/_temp_repo"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
python -m engine.orchestrator "https://github.com/<org>/<repo>.git" $runDir 50 120 $tempDir
```

Argument order:

1. `repo_url`
2. `state_run`
3. `max_files`
4. `max_kb`
5. `temp_dir`

## UI truth contract

The UI phase ladder and progress are driven by engine-emitted events from `ui_events.jsonl`:

- `FROST_PENDING` / `FROST_VERIFIED`
- `GLACIER_PENDING` / `GLACIER_VERIFIED`
- `CRYSTAL_PENDING` / `CRYSTAL_VERIFIED`
- `RESIDUE_EMPTY_LOCK` (or legacy `RESIDUE_LOCK`)

Compatibility aliases may also appear in the form `UI_EVENT:<name>`.

This keeps the UI law-coherent: render truth, never invent it.

## Output artifacts (typical)

Inside each run directory (`state/runs/<run>/`):

- `ui_events.jsonl`
- `frost_summary.json`
- `glacier_ref.json`
- `tree_snapshot.txt`
- `artifact_manifest.json`
- `artifact_hashes.json`
- `artifact/` (single crystallized root preserving repository-relative paths)
- `crystal_report.md`
- `crystal_copy_report.json` (picked vs crystallized audit; skipped reasons)
- `residue_truth.json`
- `ui_cmd_stream.log` (live orchestrator stdout captured by UI hook)
- `ai_handoff/` (+ `ai_handoff_path.txt`)

## Formal docs in this repo

- `docs/ICE_CRAWLER_ARCHITECTURE_v1_1.md` — architecture overview and invariants.
- `docs/CODEX_777_TRIADIC_BOUNDARY_EXCESS_v2_0.md` — boundary-excess principle note and engineering interpretation.
- `docs/CODEX_PHI_EXTREMAL_CONSTRAINT_AGENTICS_v1_0.md` — φ-extremal agentics principle and operational hooks.

## Troubleshooting

- **`ModuleNotFoundError` when running orchestrator:** run as module from repo root using `python -m engine.orchestrator ...`.
- **UI run appears stuck:** inspect `<run>/ui_stdout.txt` and `<run>/ui_rc.txt` for subprocess diagnostics.
- **Tkinter `no $DISPLAY` error (Linux headless):** this is an environment limitation; run with a desktop session or X server.
- **`ordinal ... could not be located` on Windows EXE:** your EXE runtime is incompatible; run `python icecrawler.py` immediately, then rebuild local EXE via `scripts/build/build_windows_exe.ps1` if needed.
- **Run folder won’t open:** ensure desktop opener is available (`explorer`, `open`, or `xdg-open`).

## License / attribution

Author attribution in architecture docs: **James Paul Jackson**.

If you need a formal OSS license, add one explicitly (for example `MIT`, `Apache-2.0`, etc.).
