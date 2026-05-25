---
name: harness-task-execution
description: Run and interpret the Luo Sisters harness workflow. Use when Codex needs to preflight task packets, run verify and bundle stages, read check profiles, inspect run bundles, interpret warn-then-gate behavior, or triage local or CI harness results.
---

# Harness Task Execution

Use this skill for packet-driven execution and harness evidence work.

## Workflow

1. Read the packet and confirm its ownership domain and required checks.
2. Run `preflight` before assuming the packet is safe to execute.
3. Run `verify` with an explicit run directory when continuity matters.
4. Read run artifacts in order: `report.json`, `summary.md`, then per-check outputs.
5. Use `bundle` and `score` when the task requires final evidence or governance status.

## Core Commands

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py preflight harness\tasks\site-smoke-check.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py verify harness\tasks\site-smoke-check.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py bundle harness\tasks\site-smoke-check.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py score
```

For one-step local execution:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\run_harness_task.py harness\tasks\site-smoke-check.json
```

## Packet Differences

- `docs`: link audit, mirror sync, and HTML-reader-oriented checks
- `page`: build, mirror sync, link audit, and browser smoke checks
- `asset`: asset validation, registry/config alignment, and path-boundary checks
- `maintenance`: repeated-issue scanning, score refresh, and governance cleanup

## Required Rules

- trust the packet and check profile as the execution contract
- prefer explicit run directories when correlating stages or comparing retries
- read CI failures through `docs/harness_ci.md`
- treat warn-then-gate as progressive enforcement, not as a reason to ignore repeated warnings

## Switch To Another Skill When

- the task becomes documentation reading or HTML structure inspection -> `project-doc-governance`
- the task becomes asset creation or transparent-output production -> `character-asset-production`
- the task becomes ownership splitting, handoff scoping, or parallel packet design -> `parallel-asset-ownership`

## When More Detail Is Needed

Read `references/harness_execution.md` for packet stages, run bundle reading order, and CI interpretation rules.
