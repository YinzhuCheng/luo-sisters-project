# Project Content Map

This document records where project content lives after the HTML-sheet, knowledge-base, asset-index, and documentation-governance restructures.

## Current State

Project content is organized across generated knowledge pages, character configuration, prompt notes, workflows, and the shared asset registry.

## Reading Hierarchy

Use this chain for documentation discovery:

```text
AGENTS.md
README.md
docs/skill_navigation.md
docs/document_governance.md
docs/content_map.md
harness/golden_principles.md
harness/ownership_map.json
docs_mirror/knowledge/navigation.md
docs_mirror/knowledge/assets.md
docs_mirror/knowledge/*.md
```

For English public pages, use the same generated structure under `en/`.

## Level 0: Source Entry Documents

- `AGENTS.md`: agent operating rules and project entry map.
- `README.md`: human quick start and build instructions.
- `docs/skill_navigation.md`: repo-local skill routing guide.
- `docs/document_governance.md`: documentation law, language separation, and HTML reading policy.
- `docs/browser_automation.md`: browser automation setup and smoke-check workflow.
- `docs/harness_ci.md`: GitHub Actions harness routing and failure-reading guide.
- `harness/golden_principles.md`: harness model and enforcement direction.
- `harness/ownership_map.json`: machine-readable write-boundary map.
- `harness/check_profiles/`: task-type verification profiles.
- `harness/task_templates/`: task packet schema and example packet.
- `harness/tasks/`: executable task packets.
- `.github/workflows/`: harness delivery-loop workflows.
- `project_data/document_catalog.json`: machine-readable document registry.

Prefer repo-local skills before reading raw workflow docs or manually assembling repeated tool sequences:

- `skills/project-doc-governance/`
- `skills/character-asset-production/`
- `skills/parallel-asset-ownership/`
- `skills/harness-task-execution/`

## Level 1: Public Showcase Pages

Default agent-readable mirrors:

- `docs_mirror/index.md`
- `docs_mirror/character_sheets/qingyou.md`
- `docs_mirror/character_sheets/arisu.md`
- `docs_mirror/knowledge/*.md`
- `docs_mirror/en/**/*.md`

Chinese root site:

- `index.html`
- `character_sheets/qingyou.html`
- `character_sheets/arisu.html`

English mirror:

- `en/index.html`
- `en/character_sheets/qingyou.html`
- `en/character_sheets/arisu.html`

## Level 2: Structured Knowledge Base

Chinese root knowledge pages:

- `knowledge/index.html`
- `knowledge/navigation.html`
- `knowledge/assets.html`
- `knowledge/characters.html`
- `knowledge/story.html`
- `knowledge/visual.html`
- `knowledge/workflow.html`

English mirror:

- `en/knowledge/index.html`
- `en/knowledge/navigation.html`
- `en/knowledge/assets.html`
- `en/knowledge/characters.html`
- `en/knowledge/story.html`
- `en/knowledge/visual.html`
- `en/knowledge/workflow.html`

Source data:

- `project_data/knowledge_base.json`
- `project_data/knowledge_base.en.json`

## Level 3: Data And Locales

- `locales/zh-CN.json`: Chinese public UI and page copy.
- `locales/en.json`: English public UI and page copy.
- `characters/qingyou.json`: Qingyou layout, palette, and asset slots.
- `characters/arisu.json`: Arisu layout, palette, and asset slots.
- `project_data/luo_sisters_overview.json`: earlier structured overview retained for continuity.

## Level 4: Production Workflow

- `workflows/asset_generation_workflow.md`: crop-to-transparent-asset workflow.
- `workflows/agent_parallel_guide.md`: multi-agent ownership and handoff rules.
- `assets/characters/qingyou/workflow/crop_manifest.csv`: Qingyou crop coordinates.
- `assets/characters/arisu/workflow/crop_manifest.csv`: Arisu crop coordinates.

## Level 5: Memory And Audit Logs

- `logs/progress_updates.csv`: work progress.
- `logs/asset_registry.csv`: asset status registry.
- `logs/issue_memory.csv`: reusable pitfalls and mitigations.

## Working Notes

- Knowledge pages and asset pages carry the current working structure.
- Edit source JSON and locale files, then run `tools/build_project_html.py`.
- If content appears missing, check this order before rewriting it: Markdown mirror, generated page, asset index, character config, asset registry, earlier overview data, then the backup under `D:\original\...`.
