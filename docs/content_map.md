# Project Content Map

This document records where the project content lives after the HTML-sheet restructure.

## Preservation Status

The current repository is not missing the first long-form guide. The first-version archive is still present at:

- `docs/luo_sisters_project_guide_v2.html`

It was compared against the backup copy at:

- `D:\original\luo_sisters_project_files\luo_sisters_project_files\docs\luo_sisters_project_guide_v2.html`

The file hashes match. The structured overview data was also compared against:

- `D:\original\luo_sisters_project_files\luo_sisters_project_files\project_data\luo_sisters_overview.json`

Those hashes match too. The current `index.html` is intentionally lighter because it now acts as the top-level display window and navigation hub.

## Navigation Hierarchy

### Level 0: Current Showcase Pages

- `index.html`: current project landing page and top-level navigation.
- `character_sheets/qingyou.html`: Luo Qingyou HTML character sheet.
- `character_sheets/arisu.html`: Luo Arisu HTML character sheet.

### Level 1: Structured Knowledge Base

New generated knowledge pages split the old archive into a navigable second level:

- `knowledge/index.html`: knowledge base index.
- `knowledge/characters.html`: eight-layer character breakdown, sister relationship, interaction examples.
- `knowledge/story.html`: story outline, chapter flow, AIGC rhythm, supporting character functions, scene hooks.
- `knowledge/visual.html`: art direction, prompt groups, expression rules, duo key visual.
- `knowledge/workflow.html`: production workflow, asset list, unified checklist, next steps.

The data source is:

- `project_data/knowledge_base.json`: page hierarchy, summaries, source anchors, and migration status.

Required chain:

- `index.html -> knowledge/index.html -> knowledge/*.html -> docs/luo_sisters_project_guide_v2.html#anchor`

### Level 2: Full First-Version Archive

Use `docs/luo_sisters_project_guide_v2.html` when you need the dense first-version content.

Important anchors:

- `#overview`: original overview.
- `#navigation`: original project navigation.
- `#characters`: maps to `knowledge/characters.html`.
- `#story`: maps to `knowledge/story.html`.
- `#visual`: maps to `knowledge/visual.html`.
- `#workflow`: maps to `knowledge/workflow.html`.
- `#asset-list`: maps to `knowledge/workflow.html#asset-list`.
- `#next`: maps to `knowledge/workflow.html#next`.

### Level 3: Structured Data And Locales

- `locales/zh-CN.json`: Chinese page text for the current generated pages.
- `locales/en.json`: English page text scaffold for future language switching.
- `characters/qingyou.json`: Qingyou layout, palette, and asset slots.
- `characters/arisu.json`: Arisu layout, palette, and asset slots.
- `project_data/knowledge_base.json`: structured knowledge base source.
- `project_data/luo_sisters_overview.json`: earlier structured overview retained for continuity.

### Level 4: Production Workflow

- `workflows/asset_generation_workflow.md`: crop-to-transparent-asset workflow.
- `workflows/agent_parallel_guide.md`: multi-agent ownership and handoff rules.
- `assets/characters/qingyou/workflow/crop_manifest.csv`: Qingyou crop coordinates.
- `assets/characters/arisu/workflow/crop_manifest.csv`: Arisu crop coordinates.

### Level 5: Memory And Audit Logs

- `logs/progress_updates.csv`: work progress.
- `logs/asset_registry.csv`: asset status registry.
- `logs/issue_memory.csv`: reusable pitfalls and mitigations.

## Content Migration Notes

- The current web pages do not duplicate every paragraph from the first archive. They link to `knowledge/`, and knowledge pages link back to the original archive anchors.
- The first archive remains the place to read the full story, prompt, workflow, and asset-list text in one page.
- `knowledge/*.html` is generated from `project_data/knowledge_base.json`; edit the JSON, then run `tools/build_project_html.py`.
- New generated pages prioritize visual presentation, responsive layout, and asset-slot tracking.
- If content appears missing, check this order before rewriting it: current page link, `knowledge/index.html`, `project_data/knowledge_base.json`, `docs/luo_sisters_project_guide_v2.html`, `project_data/luo_sisters_overview.json`, then the backup under `D:\original\...`.
