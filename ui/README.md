# ICE-CRAWLER UI

This folder contains the Tkinter UI surface for ICE-CRAWLER. The UI is an
observational control surface driven by run fossils written to
`state/runs/<run>/` and never runs git directly.

## Key behavior

- **Event truth ladder**: stage locks and reveal phrases are driven by
  `ui_events.jsonl` (`FROST_VERIFIED`, `GLACIER_VERIFIED`,
  `CRYSTAL_VERIFIED`, `RESIDUE_EMPTY_LOCK`).
- **Artifact handoff**: `ai_handoff_path.txt` provides the final output
  folder; the UI renders this path and opens it on click.
- **Completion banner**: appears when `RUN_COMPLETE` is seen in the
  run event stream.

## Animation hooks

Optional animation helpers live in `ui/animations/`. The UI imports and
starts them at startup; no engine changes are required.

## Files

- `ice_ui.py` — UI entrypoint (Tkinter)
- `animations/` — UI animation hooks
- `assets/` — UI assets (icons/backgrounds)
