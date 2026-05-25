---
name: project-doc-governance
description: Read, audit, and update this repository's Markdown and HTML documentation with low-token progressive navigation. Use when Codex needs to inspect docs, summarize HTML without loading decorative frontend layers or images, maintain document hierarchy, enforce English internal documentation with localized public web copy, or update documentation governance for the Luo Sisters project.
---

# Project Doc Governance

Use this skill for repository documentation work. Treat `.md` and `.html` as documentation.

Start with `docs/skill_navigation.md` when the task may belong to another repo-local skill.

## Reading Workflow

1. Start from `AGENTS.md`, then `README.md`, then `docs/document_governance.md`, then `docs/content_map.md`.
2. Prefer `docs_mirror/` for generated-page reading. Read one document or one mirror page first. Follow links only when the task needs the next page.
3. For raw HTML, run the bundled reader before opening the file:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/navigation.html --structure-mode
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/assets.html
python skills/project-doc-governance/scripts/read_html_doc.py character_sheets/qingyou.html --anchor workflow
```

The reader strips scripts, styles, navigation, headers, footers, and SVG/canvas decoration. It classifies links, checks local path existence, marks planned transparent outputs as `planned`, groups links by category in `--structure-mode`, and summarizes asset references. Images appear as placeholders unless `--include-images` is passed. Use it as an HTML audit tool; mirrors remain the default reading layer.

## Governance Rules

- Keep internal maintenance docs in English.
- Keep public web display copy in locale/data sources, not hardcoded in Python templates.
- Prefer a sibling repo-local skill when the task is asset production, parallel ownership, or harness execution rather than documentation work.
- Make every new doc reachable from `AGENTS.md` or `README.md`.
- Update `project_data/document_catalog.json` when adding, moving, splitting, or merging docs.
- Append reusable issues to `logs/issue_memory.csv` and progress to `logs/progress_updates.csv`.

## Switch To Another Skill When

- use `character-asset-production` for crop-to-transparent asset work and asset registration
- use `parallel-asset-ownership` for multi-agent packet boundaries and handoff discipline
- use `harness-task-execution` for packet execution, evidence bundles, and CI triage

## When More Detail Is Needed

Read `references/document_governance.md` for the full project governance policy, ownership rules, and language separation rules.
