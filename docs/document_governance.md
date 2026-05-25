# Document Governance

This document defines how agents should read, write, split, merge, and link documentation in this repository.

## Governing Law

1. Markdown and HTML are both documentation.
2. Read progressively: start at an entry document, inspect one page, then follow links only when needed.
3. HTML is a rendered documentation surface; do not load decorative frontend layers when the goal is content understanding.
4. Images in HTML are placeholders during text review. Inspect real images only when the task requires visual judgment.
5. Internal maintenance documents are English.
6. Public web copy is localized through locale or data files.
7. Every document must be reachable from `AGENTS.md` or `README.md`.
8. Generated HTML is output. Edit source data, rebuild, then verify.
9. Prefer repo-local skills before raw workflow docs or manually composing repeated tool sequences when a matching skill exists.
10. Reusable lessons belong in CSV logs and, when repeated, in skills.
11. Non-trivial work should move toward a harness task packet with declared boundaries and evidence.

## Entry Chain

Use this chain unless the user gives a more specific file:

```text
AGENTS.md
README.md
docs/skill_navigation.md
docs/document_governance.md
docs/content_map.md
harness/golden_principles.md
harness/ownership_map.json
docs_mirror/knowledge/navigation.md
docs_mirror/knowledge/assets.md or a linked child page
```

The same rule applies to the English mirror under `en/`.

Use `docs/skill_navigation.md` to choose among:

- `project-doc-governance`
- `character-asset-production`
- `parallel-asset-ownership`
- `harness-task-execution`

For GitHub Actions harness runs and artifact triage, read `docs/harness_ci.md`.

## HTML Reading Policy

Before reading a large HTML file directly, prefer its Markdown mirror under `docs_mirror/`. If raw HTML is still needed, run:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py <html-path>
```

Examples:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/navigation.html --structure-mode
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/assets.html
python skills/project-doc-governance/scripts/read_html_doc.py character_sheets/qingyou.html --anchor workflow
```

Default output includes title, readable structure, link classification, path existence checks, asset references, anchors, and image placeholders. In `--structure-mode`, links are grouped by category and planned transparent outputs remain visible without being treated as broken targets. The reader does not recursively follow links.

Use raw HTML or browser inspection when the task is frontend layout, responsive behavior, image rendering, accessibility, or link behavior.
Use Markdown mirrors when the task is content understanding, navigation, or low-token review.

For browser inspection, use the Playwright setup documented in `docs/browser_automation.md`.

## Language Separation

- Internal `.md` maintenance docs: English.
- Skill docs and references: English.
- Public Chinese site: generated at repository root from `locales/zh-CN.json` and Chinese content data.
- Public English site: generated under `en/` from `locales/en.json` and English content data.

Do not place new public-facing copy directly in `tools/build_project_html.py`. Put it in locale or project data files.

## Document Catalog

`project_data/document_catalog.json` is the registry for documentation surfaces. Update it when:

- creating a document;
- deleting a document;
- splitting or merging documents;
- changing a document's language role;
- changing whether a document is generated or source-authored;
- adding a new stable entrypoint.

Each project HTML entry should also register its mirror through `mirror_markdown`.
Skill navigation and skill reference docs are first-class internal documentation and should also be registered.

## Harness Interaction

Human-facing governance still lives in Markdown, but machine-readable governance should live in `harness/`.

- `harness/ownership_map.json` defines write-boundary domains.
- `harness/check_profiles/` describes task-type verification bundles.
- `harness/task_templates/task_packet.schema.json` defines executable task packets.
- `harness/policies/` defines enforcement defaults and evidence structure.

## Split And Merge Rules

Split a document when:

- agents regularly need only one section;
- a page mixes unrelated governance, story, asset, and build concerns;
- a subsection needs its own lifecycle or ownership.

Merge documents when:

- two files duplicate the same rules;
- a page only exists as a thin redirect without useful navigation;
- agents must always read both files together.

When splitting or merging, update links, catalog entries, and CSV logs.

## Logging

Append `logs/progress_updates.csv` for work progress. Append `logs/issue_memory.csv` when a reusable reading, encoding, localization, or governance problem appears.
