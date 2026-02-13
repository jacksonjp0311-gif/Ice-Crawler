# AI_EXPORT

`AI_EXPORT/` stores deterministic machine-readable outputs produced by ICE-CRAWLER runs for downstream tooling.

## Mini Directory
- `summary.json` — high-level run/output summary.
- `run_cmds.jsonl` — command/event stream emitted during execution.
- `ui_events.jsonl` — UI truth events (source of UI ladder state).
- `manifest_files.json` / `manifest_hashes.json` — artifact file and hash manifests.
- `artifact_manifest.json` — bundled artifact pointer list.
- `imports_index.json`, `hotspots.json`, `filetype_stats.json` — Crystal analysis outputs.

## Sequence of Events
1. Orchestrator and Crystal complete a run and emit analysis artifacts.
2. Export step writes normalized JSON/JSONL files into `AI_EXPORT/`.
3. Consumers (AI and automation) ingest these files without mutating source state.

## Interlinking Notes
- `ui_events.jsonl` mirrors the UI event contract used by `ui/`.
- Manifest and analysis files map back to Crystal/agentic outputs in `engine/` and `agentics/`.
