# Project Content Map

This document records where project content lives after the HTML-sheet, knowledge-base, and documentation-governance restructures.

## Preservation Status

The first long-form Chinese guide is preserved at:

- `docs/luo_sisters_project_guide_v2.html`

The current showcase is intentionally lighter. Long-form material now lives in generated knowledge pages and source data, while the historical archive remains available for verification.

## Reading Hierarchy

Use this chain for documentation discovery:

```text
AGENTS.md
README.md
docs/document_governance.md
docs/content_map.md
knowledge/index.html
knowledge/*.html
docs/luo_sisters_project_guide_v2.html#anchor
```

For English public pages, use the same generated structure under `en/`.

## Level 0: Source Entry Documents

- `AGENTS.md`: agent operating rules and project entry map.
- `README.md`: human quick start and build instructions.
- `docs/document_governance.md`: documentation law, language separation, and HTML reading policy.
- `project_data/document_catalog.json`: machine-readable document registry.

## Level 1: Public Showcase Pages

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
- `knowledge/characters.html`
- `knowledge/story.html`
- `knowledge/visual.html`
- `knowledge/workflow.html`

English mirror:

- `en/knowledge/index.html`
- `en/knowledge/characters.html`
- `en/knowledge/story.html`
- `en/knowledge/visual.html`
- `en/knowledge/workflow.html`

Source data:

- `project_data/knowledge_base.json`
- `project_data/knowledge_base.en.json`

## Level 3: Historical Archive

Use `docs/luo_sisters_project_guide_v2.html` when source verification or dense first-version content is needed.

Important anchors:

- `#overview`: original overview.
- `#navigation`: original project navigation.
- `#characters`: maps to `knowledge/characters.html`.
- `#story`: maps to `knowledge/story.html`.
- `#visual`: maps to `knowledge/visual.html`.
- `#workflow`: maps to `knowledge/workflow.html`.
- `#asset-list`: maps to `knowledge/workflow.html#asset-list`.
- `#next`: maps to `knowledge/workflow.html#next`.

## Level 4: Data And Locales

- `locales/zh-CN.json`: Chinese public UI and page copy.
- `locales/en.json`: English public UI and page copy.
- `characters/qingyou.json`: Qingyou layout, palette, and asset slots.
- `characters/arisu.json`: Arisu layout, palette, and asset slots.
- `project_data/luo_sisters_overview.json`: earlier structured overview retained for continuity.

## Level 5: Production Workflow

- `workflows/asset_generation_workflow.md`: crop-to-transparent-asset workflow.
- `workflows/agent_parallel_guide.md`: multi-agent ownership and handoff rules.
- `assets/characters/qingyou/workflow/crop_manifest.csv`: Qingyou crop coordinates.
- `assets/characters/arisu/workflow/crop_manifest.csv`: Arisu crop coordinates.

## Level 6: Memory And Audit Logs

- `logs/progress_updates.csv`: work progress.
- `logs/asset_registry.csv`: asset status registry.
- `logs/issue_memory.csv`: reusable pitfalls and mitigations.

## Migration Notes

- Generated pages do not duplicate every paragraph from the first archive.
- Knowledge pages link back to original archive anchors.
- Edit source JSON and locale files, then run `tools/build_project_html.py`.
- If content appears missing, check this order before rewriting it: generated page, knowledge source data, historical archive, earlier overview data, then the backup under `D:\original\...`.
