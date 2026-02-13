# ICE-CRAWLER Evolution Roadmap

This roadmap captures practical next-step improvements to evolve ICE-CRAWLER across backend and frontend while preserving Frost/Glacier/Crystal invariants.

## Backend improvements

1. **Structured command runner abstraction**
   - Centralize subprocess execution (`run`, `check_call`, streaming) in one engine utility.
   - Standardize hidden-window behavior on Windows, timeout policy, and error envelopes.

2. **Per-phase timing + resource telemetry**
   - Write `phase_metrics.json` in each run dir with duration, selected file count, skipped counts, and return code summaries.
   - Keep deterministic field ordering for stable downstream parsing.

3. **Glacier selection explainability**
   - Emit `glacier_selection_report.json` with bucket counts (`frost/glacier/crystal`) and selected examples.
   - Makes bounded file selection auditable and tunable.

4. **Crystal integrity extensions**
   - Add optional reproducibility check mode that re-hashes copied artifacts and reports mismatch deltas.
   - Preserve read-only output contract in run artifacts.

5. **Agentic guardrails**
   - Add max-task cap and per-task size diagnostics in agentic outputs.
   - Prevent runaway partitioning on giant repos.

## Frontend improvements

1. **Live phase duration badges**
   - Show elapsed time per phase beside ladder status.
   - Source only from run artifacts/events, no UI-invented state.

2. **Run health panel**
   - Add compact indicators for `ui_rc.txt`, residue status, and artifact count.
   - Keep this observational-only and driven by run fossils.

3. **Command stream filtering**
   - Add UI toggles to filter CMD TRACE by phase (`frost`, `glacier`, `crystal`, `agentic`).
   - Parse from `run_cmds.jsonl` notes only.

4. **Post-run summary export**
   - Add an "Export summary" action that emits a markdown report into the active run folder.
   - Include phase events, counts, and handoff pointers.

5. **Accessibility/theme enhancements**
   - Provide alternate high-contrast palette and larger default text mode.
   - Keep style logic centralized in `ui/design/theme.py`.

## Recommended implementation order

1. Backend command runner abstraction + metrics artifacts.
2. Frontend run health panel consuming those artifacts.
3. Glacier/Crystal explainability and UI surfacing.
4. Agentic guardrails and richer trace filters.
