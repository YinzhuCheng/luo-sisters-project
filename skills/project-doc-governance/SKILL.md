---
name: project-doc-governance
description: Read, audit, and update this repository's Markdown and HTML documentation with low-token progressive navigation. Use when Codex needs to inspect docs, summarize HTML without loading decorative frontend layers or images, maintain document hierarchy, enforce English internal documentation with localized public web copy, or update documentation governance for the Luo Sisters project.
---

# Project Doc Governance

Use this skill for repository documentation work. Treat `.md` and `.html` as documentation.

## Reading Workflow

1. Start from `AGENTS.md`, then `README.md`, then `docs/document_governance.md`, then `docs/content_map.md`.
2. Read one document or HTML page first. Follow links only when the task needs the next page.
3. For HTML, run the bundled reader before opening the raw file:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py index.html
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/visual.html --anchor prompt-base
python skills/project-doc-governance/scripts/read_html_doc.py docs/luo_sisters_project_guide_v2.html#characters
```

The reader strips scripts, styles, navigation, headers, footers, and SVG/canvas decoration. Images appear as placeholders unless `--include-images` is passed.

## Governance Rules

- Keep internal maintenance docs in English.
- Keep public web display copy in locale/data sources, not hardcoded in Python templates.
- Preserve the historical Chinese archive at `docs/luo_sisters_project_guide_v2.html`.
- Make every new doc reachable from `AGENTS.md` or `README.md`.
- Update `project_data/document_catalog.json` when adding, moving, splitting, or merging docs.
- Append reusable issues to `logs/issue_memory.csv` and progress to `logs/progress_updates.csv`.

## When More Detail Is Needed

Read `references/document_governance.md` for the full project governance policy, ownership rules, and language separation rules.
