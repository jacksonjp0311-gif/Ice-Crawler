# ICE CRAWLER 1.1 — Software Architecture

Author: James Paul Jackson  
Date: January 2026

## Purpose

This architecture document defines how ICE-CRAWLER implements triadic zero-trace repository ingestion:

1. Frost → telemetry-only scout
2. Glacier → ephemeral materialization
3. Crystal → deterministic artifact crystallization
4. Residue lock → teardown confirmation (`ρ = ∅`)

The UI is intentionally **observational** and only renders engine-emitted truth.

## What this is

- A software architecture for containment-first ingestion.
- A reproducible scaffold for bounded AI/code-intelligence context creation.
- A validation-oriented design emphasizing deterministic artifacts and teardown proofs.

## What this is not

- Not a malware detector.
- Not a universal security claim.
- Not a fourth ingestion phase in the UI.

## Event truth surface

Canonical run progression uses these events:

- `FROST_PENDING` → `FROST_VERIFIED`
- `GLACIER_PENDING` → `GLACIER_VERIFIED`
- `CRYSTAL_PENDING` → `CRYSTAL_VERIFIED`
- `RESIDUE_EMPTY_LOCK`
- `RUN_COMPLETE`

Compatibility aliases may also appear as `UI_EVENT:<name>` entries.

## Core invariant

Post-run residue must be empty except explicit retained artifacts:

`ρ_post-run = ∅`

## Determinism contract

For identical `(repo, revision, config)` inputs, output artifacts should remain stable in file set and hash structure.
- Crystal stores selected files under a **single artifact root** while preserving repository-relative paths to prevent flattening collisions.

## Optional agentic hooks (non-invasive)

An opt-in agentic layer can attach to the run **without modifying core engines**:

- **Frost hook**: partitions `git ls-remote` ref metadata into φ-scaled tasks.
- **Crystal hook**: partitions the artifact manifest into φ-scaled tasks.

Hooks run before Glacier and before the residue lock when enabled. They emit artifacts into `<run>/frost_agentic/` and `<run>/agentic/` respectively and do not alter core selection logic.
