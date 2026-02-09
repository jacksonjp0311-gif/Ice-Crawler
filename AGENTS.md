# Agent Instructions (Ice-Crawler)

## Scope
These instructions apply to the entire repository.

## Workflow
- Prefer additive, non-invasive changes that preserve Frost/Glacier/Crystal invariants.
- Keep UI changes event-driven; do not invent state outside `ui_events.jsonl`.
- Update documentation alongside new artifacts or run outputs.

## Notes
- Ensure new run artifacts are written under the run directory and respect deterministic ordering.
