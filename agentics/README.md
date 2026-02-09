# Φ-Extremal Agentics (Ice-Crawler Extension)

This directory adds a **separate, opt-in agentic layer** that hooks into an existing ICE-CRAWLER run without modifying core engines.

## What it does

- Reads a completed run's `artifact_manifest.json`.
- Computes φ-scaled partitions based on file sizes.
- Emits agent task bundles into `<run>/agentic/` for downstream analysis.

## How to run

```bash
python -m agentics.pipeline state/runs/<run_id>
```

Optional override for bounded size (KB per partition):

```bash
python -m agentics.pipeline state/runs/<run_id> --max-kb 160
```

## Outputs

- `agentic/agent_tasks.json` — task list with file assignments.
- `agentic/agent_index.json` — summary, φ constants, and oversize list.
- `agentic/agent_prompt.md` — prompt template for agents.

## Notes

- This is a **hook-in postprocessor**: it consumes artifacts produced by the existing pipeline.
- Oversize files are recorded separately so they can be handled manually or by specialized agents.
