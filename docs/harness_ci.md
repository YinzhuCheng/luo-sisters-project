# Harness CI

This repository uses GitHub Actions as the delivery loop for the harness control plane.

## Workflows

- `harness-docs.yml`: docs governance packet
- `harness-pages.yml`: knowledge and public page packets
- `harness-assets.yml`: character asset packets and shared registry packet
- `harness-maintenance.yml`: scheduled maintenance packet and score snapshot

## Local Mirror

Use the local runner wrapper when you want the same staged flow outside GitHub:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\run_harness_task.py harness\tasks\site-smoke-check.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\run_harness_task.py harness\tasks\harness-maintenance.json --score
```

The wrapper creates one stable run directory, then runs:

1. `preflight`
2. `verify`
3. `bundle`
4. optional `score`

Docs and page packets also run Markdown mirror synchronization checks through `tools/build_html_markdown_mirror.py --check`.

You can also recompute the repository quality snapshot directly:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py score
```

## Warn Then Gate

The default policy lives in `harness/policies/warn_then_gate.json`.

Blocking failures:

- invalid packet shape
- ownership boundary violations
- conflicting allowed and forbidden paths
- broken public local links
- cross-character asset config or registry drift

Warnings:

- low quality score
- evidence gaps on non-critical maintenance work
- docs or page coverage gaps
- planned asset outputs that are not produced yet

## Issue Promotion

`logs/issue_memory.csv` now tracks:

- `issue_key`
- `policy_ref`
- `check_ref`
- `promotion_level`

The maintenance harness scans those fields and applies the promotion ladder from `harness/policies/warn_then_gate.json`:

1. repeated issue -> policy reference
2. repeated again -> verify coverage
3. repeated after verify coverage -> review for blocking gate

## Failure Reading Order

When CI fails or warns, read in this order:

1. workflow summary in GitHub Actions
2. `report.json` inside the uploaded `logs/harness_runs/<timestamp>-<task-id>/`
3. `summary.md` in the same run directory
4. artifacts under `artifacts/`
5. the packet JSON in `harness/tasks/`
6. the matching check profile in `harness/check_profiles/`
7. `harness/policies/warn_then_gate.json`

## Artifact Convention

Each workflow uploads the matching run directory under `logs/harness_runs/`.

Expected top-level files:

- `preflight.json`
- `verify.json`
- `report.json`
- `summary.md`

Maintenance runs may also include `score.json`.
