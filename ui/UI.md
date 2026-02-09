# ICE-CRAWLER UI Notes

## Event-driven truth

The UI reads only fossil artifacts emitted by the engine layer:

- `ui_events.jsonl`
- `ai_handoff_path.txt`
- `ui_stdout.txt` / `ui_rc.txt` (debug)

All visual state is derived from those events and files.

## Stage reveals

After a stage verifies, a short delay reveals state-language next to the
stage name. This is UI-only and does not alter engine flow.

## Completion banner

A bordered orange banner appears after `RUN_COMPLETE` is observed.
The banner is a UI indicator and does not alter any run artifacts.

## Agents deployed banner

A blue-bordered **AGENTS DEPLOYED** banner appears only when agentic hooks
report success (`AGENTIC_FROST_VERIFIED` or `AGENTIC_CRYSTAL_VERIFIED`).
Both banners are rendered alongside the ladder to avoid layout shifts in the output panel.
