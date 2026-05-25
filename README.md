# Luo Qingyou x Luo Arisu Character Project

This repository is an original anime-style character project designed for long-running Codex and multi-agent collaboration. The current system turns full character sheets into structured web pages, strict asset folders, reference-crop workflows, bilingual public pages, and reusable documentation memory.

## Quick Entry

1. Read `AGENTS.md` for agent rules.
2. Read `docs/document_governance.md` for documentation policy.
3. Read `docs/content_map.md` for the content hierarchy.
4. Open `index.html` for the Chinese public showcase.
5. Open `en/index.html` for the English mirror.
6. Open `knowledge/index.html` or `en/knowledge/index.html` for structured knowledge pages.
7. Use `skills/project-doc-governance/scripts/read_html_doc.py` before reading large HTML files.

## Build The Website

Build all public locales:

```bash
python tools/build_project_html.py
```

Build one locale:

```bash
python tools/build_project_html.py --locale zh-CN
python tools/build_project_html.py --locale en
```

Generated outputs:

- `index.html`
- `character_sheets/qingyou.html`
- `character_sheets/arisu.html`
- `knowledge/index.html`
- `knowledge/characters.html`
- `knowledge/story.html`
- `knowledge/visual.html`
- `knowledge/workflow.html`
- `en/index.html`
- `en/character_sheets/qingyou.html`
- `en/character_sheets/arisu.html`
- `en/knowledge/*.html`

## Low-Token HTML Reading

Do not open large HTML files directly unless the task is layout debugging. Summarize one page or one anchor first:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py index.html
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/visual.html --anchor prompt-base
python skills/project-doc-governance/scripts/read_html_doc.py docs/luo_sisters_project_guide_v2.html#characters
```

The reader hides scripts, styles, navigation, headers, footers, SVG/canvas decoration, and image payloads. Images are represented as placeholders until visual inspection is needed.

## Data And Localization

- `locales/zh-CN.json`: Chinese public UI and page copy.
- `locales/en.json`: English public UI and page copy.
- `project_data/knowledge_base.json`: Chinese generated knowledge content.
- `project_data/knowledge_base.en.json`: English generated knowledge content.
- `characters/qingyou.json`, `characters/arisu.json`: character asset slots, palettes, layout, and paths.
- `project_data/document_catalog.json`: machine-readable documentation registry.

Keep internal maintenance docs in English. Keep public display copy in locale or data files. Do not hardcode public-facing copy in Python templates.

## Asset Structure

Each character has an isolated root:

```text
assets/characters/qingyou/
assets/characters/arisu/
```

Each root keeps the same structure:

```text
source_sheet/
crops/
generated/chroma/<asset_type>/
generated/transparent/<asset_type>/
generated/rejected/
prompts/
workflow/
```

Current asset types:

- `standing`
- `expressions`
- `turnaround`
- `clothing`
- `accessories`
- `props`
- `details`
- `cg`

## Image Workflow

1. Crop references from `source_sheet/`:

```bash
python tools/crop_from_sheet.py --character all --force
```

2. Use each crop as a reference to regenerate a clean, textless, borderless image on flat `#ff00ff`.
3. If a crop is skewed or lacks context, inspect the full `source_sheet/` image before changing the crop manifest.
4. Save chroma sources under `generated/chroma/<asset_type>/`.
5. Remove background:

```bash
python tools/remove_chroma_batch.py --character qingyou --asset-type props
```

6. Validate:

```bash
python tools/validate_assets.py
```

## Content Preservation

- `index.html` is a lightweight public showcase, not the complete long-form archive.
- `knowledge/*.html` and `en/knowledge/*.html` are generated structured knowledge pages.
- `docs/luo_sisters_project_guide_v2.html` is the preserved historical Chinese archive.
- `docs/content_map.md` explains where old and new content live.

## Project Memory

All agents should maintain CSV logs:

- `logs/progress_updates.csv`: work progress.
- `logs/asset_registry.csv`: asset status registry.
- `logs/issue_memory.csv`: reusable pitfalls and mitigations.

These logs are future skill material.
