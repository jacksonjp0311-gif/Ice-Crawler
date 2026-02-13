# artifact

`artifact/` contains project-level artifact bundle metadata tracked in-repo.

## Mini Directory
- `bundles/artifact_manifest.json` — baseline bundle manifest reference.

## Sequence of Events
1. Crystal/run outputs are generated under run state directories.
2. Bundle metadata snapshots can be copied or promoted into `artifact/bundles/`.
3. Tracked metadata is used for reproducible handoff and audit references.

## Interlinking Notes
- Distinct from per-run `state/runs/...` outputs (runtime fossils).
- Manifest structure aligns with Crystal artifact naming conventions.
