# Harness Golden Principles

This repository uses harness engineering to make agent work legible, bounded, and repeatable.

## Core Model

The harness has four layers:

1. `Context`: entrypoints, catalogs, ownership, templates, and source-of-truth documents.
2. `Constraint`: machine-readable policies, task packet validation, boundary checks, and required evidence.
3. `Convergence`: scoring, recurring cleanup, issue-to-rule promotion, and maintenance tasks.
4. `Delivery loop`: local commands, CI jobs, run artifacts, and phase-by-phase pushes.

## Working Rules

- Every non-trivial task should be represented as a task packet.
- A task packet must declare where it may write.
- A task packet must point to checks and evidence outputs before execution starts.
- Generated HTML remains output; source data and harness metadata are the long-term editing surface.
- Character asset ownership stays strictly separated by character root.
- Knowledge, docs, pages, and assets should be discoverable from stable entrypoints before they are expanded.

## Enforcement Direction

This repository uses `warn then gate`.

- Structural corruption should fail immediately.
- Coverage and quality gaps should begin as warnings.
- Repeated failures should be promoted from memory -> policy -> verify check -> blocking gate.

## Expected Outcomes

When the harness is healthy:

- agents can find the right source quickly;
- tasks have narrow, auditable boundaries;
- checks are predictable and reusable;
- outputs carry evidence;
- repeated repository drift gets harder over time.
