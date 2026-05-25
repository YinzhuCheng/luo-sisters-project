# Skill Navigation

This document is the repo-local skill index for the Luo Sisters project. Prefer a matching repo-local skill before reading raw workflows, large HTML pages, or running tools one by one.

## Routing Table

| Task Shape | Preferred Skill | Use It When |
| --- | --- | --- |
| doc reading, HTML audit, catalog updates | `project-doc-governance` | you need low-token reading, mirror-first navigation, or documentation governance |
| asset production | `character-asset-production` | you are creating, revising, registering, or validating character assets |
| multi-agent boundary or handoff | `parallel-asset-ownership` | you need packet scoping, ownership checks, or serialized shared-log work |
| packet execution, CI, evidence | `harness-task-execution` | you are running harness stages, reading run bundles, or triaging warnings/failures |

## Skill Index

### `project-doc-governance`

- Trigger: documentation reading, HTML summary, mirror-first navigation, doc governance edits
- Prefer over raw docs/tools when the task is understanding structure rather than changing layout
- Primary files and commands:
  - `skills/project-doc-governance/scripts/read_html_doc.py`
  - `docs/document_governance.md`
  - `docs/content_map.md`
  - `docs_mirror/`
- Expected output: a reading route, structured summary, or governance-safe doc update
- Switch next:
  - to `character-asset-production` for actual asset work
  - to `parallel-asset-ownership` for multi-agent scoping
  - to `harness-task-execution` for packet and CI execution

### `character-asset-production`

- Trigger: crop inspection, chroma generation, transparent PNG production, asset registration, validation
- Prefer over raw workflows/tools when the task is actual asset output rather than just discussing process
- Primary files and commands:
  - `workflows/asset_generation_workflow.md`
  - `characters/<character>.json`
  - `logs/asset_registry.csv`
  - `python tools/crop_from_sheet.py --character all --force`
  - `python tools/remove_chroma_batch.py --character <character> --asset-type <type>`
  - `python tools/validate_assets.py`
- Expected output: correctly placed, versioned asset outputs plus updated CSV memory
- Switch next:
  - to `parallel-asset-ownership` when another agent must take a neighboring scope
  - to `harness-task-execution` when a packet or CI run becomes the main execution surface
  - to `project-doc-governance` when the task becomes doc or mirror maintenance

### `parallel-asset-ownership`

- Trigger: multi-agent splitting, task-packet narrowing, ownership review, serialized shared-log planning, handoff
- Prefer over raw workflows/tools when the risk is path collision, shared CSV overlap, or fuzzy task scope
- Primary files and commands:
  - `workflows/agent_parallel_guide.md`
  - `harness/ownership_map.json`
  - `harness/tasks/`
  - `logs/progress_updates.csv`
  - `logs/asset_registry.csv`
- Expected output: a clear ownership boundary, packet scope, and handoff-ready next step
- Switch next:
  - to `character-asset-production` for the actual asset work
  - to `harness-task-execution` for packet running and evidence
  - to `project-doc-governance` for doc updates caused by the handoff plan

### `harness-task-execution`

- Trigger: preflight, verify, bundle, score, local run-bundle reading, CI triage
- Prefer over raw CLI usage when the task needs consistent packet interpretation and evidence reading order
- Primary files and commands:
  - `tools/harness_cli.py`
  - `tools/run_harness_task.py`
  - `tools/harness_warn_then_gate.py`
  - `docs/harness_ci.md`
  - `harness/check_profiles/*.json`
  - `harness/tasks/*.json`
- Expected output: packet-safe execution, interpretable evidence, and correct next action on pass/warn/fail
- Switch next:
  - to `character-asset-production` if the packet leads into asset production
  - to `parallel-asset-ownership` if the packet must be narrowed or handed off
  - to `project-doc-governance` if the issue is really in docs, mirrors, or catalog structure

## Usage Rule

Start with the narrowest matching skill. If the task changes shape, switch skills instead of stretching one skill across unrelated concerns.
