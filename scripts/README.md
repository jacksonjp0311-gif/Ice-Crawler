# scripts

`scripts/` contains launcher and build helper scripts.

## Mini Directory
- `launchers/icecrawler.sh` — shell launcher wrapper.
- `launchers/icecrawler.ps1` — PowerShell launcher wrapper.
- `build/` — packaging/build helper scripts (for example Windows EXE build flows).

## Sequence of Events
1. Operator picks platform-specific launcher/build script.
2. Script delegates to canonical project entrypoint (`icecrawler.py`) or packaging flow.
3. Runtime behavior remains governed by `engine/` + `ui/` contracts.

## Interlinking Notes
- Wrappers are convenience layers; they do not replace orchestrator/UI truth contracts.
- Keep script changes aligned with root `README.md` launch instructions.
