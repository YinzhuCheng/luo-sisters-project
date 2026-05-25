---
name: parallel-asset-ownership
description: Split Luo Sisters work safely across multiple agents. Use when Codex needs to choose packet boundaries, isolate one character or asset-type subtree, serialize shared log work, prepare handoffs, or prevent cross-character path mistakes during parallel execution.
---

# Parallel Asset Ownership

Use this skill when more than one agent may touch related assets, logs, packets, or page outputs.

## Workflow

1. Start from the task packet or create a narrow packet before parallel execution begins.
2. Confirm the ownership domain and allowed paths before editing anything.
3. Split work by character root or by one transparent asset subtree inside one character root.
4. Keep shared CSV and shared harness maintenance work serialized.
5. End with a clear handoff note instead of silently broadening scope.

## Core Files

- `harness/ownership_map.json`
- `harness/tasks/`
- `workflows/agent_parallel_guide.md`
- `logs/progress_updates.csv`
- `logs/asset_registry.csv`
- `logs/issue_memory.csv`

## Required Rules

- Parallel packets must have disjoint `allowed_paths`.
- Asset work should stay inside one character root or one asset-type subtree.
- Shared registry or maintenance packets should not run in parallel with asset packets still touching the same CSV files.
- When a task drifts into another ownership domain, stop and hand off instead of expanding the packet.
- Record packet ids in notes when shared logs are updated.

## Handoff

Leave:

- packet id
- owned paths
- remaining blocked paths or shared files
- validation state
- unresolved issues
- next recommended packet or skill

## Switch To Another Skill When

- the task becomes actual crop or transparent asset production -> `character-asset-production`
- the task becomes doc reading, mirror inspection, or HTML audit -> `project-doc-governance`
- the task becomes harness preflight, verify, bundle, score, or CI reading -> `harness-task-execution`

## When More Detail Is Needed

Read `references/parallel_ownership.md` for packet-first rules, serialized shared work, and handoff discipline.
