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

## Repository layout

- `engine/` — phase engines and orchestrator.
- `ui/` — Tkinter UI and UI registry metadata.
- `state/runs/<run_...>/` — per-run fossils and artifacts.
- `artifact/` — project-level artifact bundle metadata.

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

## Launch from repository root

Use the root launchers so operators can start the UI from the main project directory:

- `launch_ice_crawler.py` (cross-platform Python launcher)
- `launch_ice_crawler.sh` (Bash launcher)
- `launch_ice_crawler.ps1` (PowerShell launcher)

### EXE behavior by platform

- **Windows:** double-click `IceCrawler.exe` in repo root (snowflake-branded app window title: `ICE-CRAWLER ❄`).
- **macOS/Linux:** `.exe` is a Windows binary; use the launch scripts above or run `python ui/ice_ui.py`.

## Running the UI

### Bash (Linux/macOS)

```bash
python ui/ice_ui.py
```

Then paste a repository URL and click **Run**.

### PowerShell (Windows)

```powershell
python .\ui\ice_ui.py
```

Then paste a repository URL and click **Run**.

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
- `crystal_report.md`
- `residue_truth.json`
- `ai_handoff/` (+ `ai_handoff_path.txt`)

## Formal docs in this repo

- `docs/ICE_CRAWLER_ARCHITECTURE_v1_1.md` — architecture overview and invariants.
- `docs/CODEX_777_TRIADIC_BOUNDARY_EXCESS_v2_0.md` — boundary-excess principle note and engineering interpretation.

## Troubleshooting

- **`ModuleNotFoundError` when running orchestrator:** run as module from repo root using `python -m engine.orchestrator ...`.
- **UI run appears stuck:** inspect `<run>/ui_stdout.txt` and `<run>/ui_rc.txt` for subprocess diagnostics.
- **Tkinter `no $DISPLAY` error (Linux headless):** this is an environment limitation; run with a desktop session or X server.
- **Run folder won’t open:** ensure desktop opener is available (`explorer`, `open`, or `xdg-open`).

## License / attribution

Author attribution in architecture docs: **James Paul Jackson**.

If you need a formal OSS license, add one explicitly (for example `MIT`, `Apache-2.0`, etc.).
