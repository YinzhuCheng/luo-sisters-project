# Harness Tasks

This directory stores executable task packets.

## Current Status

- Phase 1 creates the control plane and schemas.
- Phase 3 backfills real repository work into concrete task packets.

## Rule

Every non-trivial docs, page, asset, or maintenance task should eventually land here as a packet that declares:

- intent
- write boundary
- required inputs
- expected outputs
- required checks
- evidence expectations

Task packets are machine-readable execution contracts, not just notes.
