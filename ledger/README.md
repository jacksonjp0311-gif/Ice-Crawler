# ledger

`ledger/` contains append-only run ledger records.

## Mini Directory
- `ice_crawler_ledger.jsonl` — chronological JSONL run checkpoints and completion facts.

## Sequence of Events
1. Pipeline checkpoints are emitted during/after orchestrated runs.
2. Records are appended to `ice_crawler_ledger.jsonl` in chronological order.
3. Ledger entries provide historical traceability across executions.

## Interlinking Notes
- Complements per-run event logs (`ui_events.jsonl`) by preserving cross-run history.
- Supports audit and residue-proof review workflows.
