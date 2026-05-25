# Harness Tasks

This directory stores executable task packets.

## Current Status

- Phase 1 creates the control plane and schemas.
- Phase 3 backfills real repository work into concrete task packets.

## Current Packets

- `docs-governance-maintenance.json`
- `knowledge-page-structure.json`
- `site-smoke-check.json`
- `qingyou-asset-batch.json`
- `arisu-asset-batch.json`
- `asset-registry-sync.json`
- `harness-maintenance.json`

Read packet JSON directly when you need exact write boundaries or check requirements.

## Rule

Every non-trivial docs, page, asset, or maintenance task should eventually land here as a packet that declares:

- intent
- write boundary
- required inputs
- expected outputs
- required checks
- evidence expectations

Task packets are machine-readable execution contracts, not just notes.
