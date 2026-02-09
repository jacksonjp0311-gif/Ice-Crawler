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

## Ladder update timing

The ladder and timeline update once the run completes, keeping the ladder state stable during execution.

## Handoff badge

An orange handoff badge appears after `RUN_COMPLETE` and links to the `ai_handoff` folder when present.

## Agents status row

The blue **AGENTS** status row appears only when agentic hooks
write success artifacts (`agentic/AGENTS_OK.json`) or failure artifacts (`agentic/AGENTS_FAIL.json`).
Both banners are rendered alongside the ladder to avoid layout shifts in the output panel.

The output residue panel mirrors the agentic status once per transition:

- `[ Agents OK — agentic/AGENTS_OK.json ]`
- `[ Agents FAILED — agentic/AGENTS_FAIL.json ]`

## Run thread box

A blue "RUN THREAD" panel appears to the right of the output residue section. It streams the last events from `ui_events.jsonl` so operator context is visible without spawning external consoles.

## Command trace box

A blue "CMD TRACE" panel appears above the run thread. It tails `run_cmds.jsonl` to show the commands executed by engines/agent hooks.

## Run console

The "RUN CONSOLE" panel sits under the submit button and streams live stdout/stderr from the orchestrator in a scrollable, fixed-height box. No external terminals are spawned.

## Headless execution

Engine subprocesses are launched with hidden window flags so no CMD/PowerShell windows appear during runs.
