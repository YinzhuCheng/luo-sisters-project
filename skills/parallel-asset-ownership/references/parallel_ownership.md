# Parallel Asset Ownership Reference

## Use This Skill For

- deciding whether work can run in parallel
- narrowing or reviewing a task packet
- choosing character or asset-type ownership boundaries
- deciding when shared log work must be serialized
- writing handoff notes for the next agent

## Primary Inputs

- `harness/ownership_map.json`
- `harness/tasks/*.json`
- `workflows/agent_parallel_guide.md`
- `logs/asset_registry.csv`
- `logs/progress_updates.csv`
- `logs/issue_memory.csv`

## Safe Split Patterns

Preferred parallel patterns:

- one character per agent
- one asset type per agent inside one character root
- one docs packet and one page packet in separate ownership domains

Avoid:

- two agents editing the same character registry rows at once
- asset work and registry-sync work touching the same CSV files in parallel
- broad packets that span docs, page generation, and asset production together

## Serialized Work

Treat these as shared and serialize them when active:

- `harness/tasks/asset-registry-sync.json`
- `harness/tasks/harness-maintenance.json`
- direct edits to shared CSV logs when another packet is still actively using them

## Handoff Standard

Every handoff should name:

- packet id
- owned paths
- touched CSV files
- validation result
- reusable issues or traps
- next expected skill or packet

## Escalation Rule

If you discover that the task needs paths outside the current domain, do not quietly continue. Narrow the current work, log the state, and hand off to a new packet or owner.
