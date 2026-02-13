# Engine Overview

The `engine/` package is the execution core for ICE-CRAWLER.

## Mini Directory
- `frost.py` — resolves remote telemetry/metadata without cloning full history.
- `glacier.py` — performs bounded shallow materialization and deterministic selection.
- `crystal.py` — emits deterministic analysis artifacts and manifests.
- `orchestrator.py` — canonical pipeline entrypoint wiring all phases.
- `active/engine_active.py` — current active engine metadata/state export.
- `agents/crystal_agents/` — Crystal-side analysis agents (imports, hotspots, filetypes, README synthesis).
- `roles/` — role-specialized Crystal engine variants.
- `_quarantine/` — archived/experimental assets outside active pipeline flow.

## Sequence of Events
1. `orchestrator.py` initializes run paths and event emission.
2. Frost gathers repository telemetry and baseline references.
3. Glacier clones/materializes a bounded working set deterministically.
4. Crystal computes outputs (`imports_index`, `hotspots`, manifests, stats).
5. Run artifacts and truth events are finalized for UI and downstream consumers.

## Interlinking Notes
- `orchestrator.py` is the only intended pipeline entrypoint.
- Engine outputs are consumed by `ui/`, `AI_EXPORT/`, and optional `agentics/` hooks.
- Deterministic ordering and residue constraints are part of the engine contract.
