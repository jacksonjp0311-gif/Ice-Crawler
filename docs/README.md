# docs

`docs/` stores architecture and constraints documentation for ICE-CRAWLER.

## Mini Directory
- `ICE_CRAWLER_ARCHITECTURE_v1_1.md` — core architecture and execution model.
- `CODEX_777_TRIADIC_BOUNDARY_EXCESS_v2_0.md` — triadic boundary constraints.
- `CODEX_PHI_EXTREMAL_CONSTRAINT_AGENTICS_v1_0.md` — optional agentic Φ-extremal constraints.

## Sequence of Events
1. Engine/UI behavior is defined and constrained by these documents.
2. Code changes in `engine/`, `ui/`, and `agentics/` should preserve documented invariants.
3. Documentation is updated when architectural or law-level behavior changes.

## Interlinking Notes
- Serves as the human-readable contract for implementation in `engine/` and `ui/`.
- Supports auditability and deterministic behavior claims across runs.
