# Document Governance

This document defines how agents should read, write, split, merge, and link documentation in this repository.

## Governing Law

1. Markdown and HTML are both documentation.
2. Read progressively: start at an entry document, inspect one page, then follow links only when needed.
3. HTML is a rendered documentation surface; do not load decorative frontend layers when the goal is content understanding.
4. Images in HTML are placeholders during text review. Inspect real images only when the task requires visual judgment.
5. Internal maintenance documents are English.
6. Public web copy is localized through locale or data files.
7. The Chinese historical archive is preserved as source evidence and must not be overwritten by translation.
8. Every document must be reachable from `AGENTS.md` or `README.md`.
9. Generated HTML is output. Edit source data, rebuild, then verify.
10. Reusable lessons belong in CSV logs and, when repeated, in skills.

## Entry Chain

Use this chain unless the user gives a more specific file:

```text
AGENTS.md
README.md
docs/document_governance.md
docs/content_map.md
knowledge/index.html
linked child page or old archive anchor
```

The same rule applies to the English mirror under `en/`.

## HTML Reading Policy

Before reading a large HTML file directly, run:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py <html-path>
```

Examples:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py index.html
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/visual.html --anchor prompt-base
python skills/project-doc-governance/scripts/read_html_doc.py docs/luo_sisters_project_guide_v2.html#characters
```

Default output includes title, readable structure, links, anchors, and image placeholders. It does not recursively follow links.

Use raw HTML or browser inspection when the task is frontend layout, responsive behavior, image rendering, accessibility, or link behavior.

## Language Separation

- Internal `.md` maintenance docs: English.
- Skill docs and references: English.
- Public Chinese site: generated at repository root from `locales/zh-CN.json` and Chinese content data.
- Public English site: generated under `en/` from `locales/en.json` and English content data.
- Historical archive: Chinese, preserved at `docs/luo_sisters_project_guide_v2.html`.

Do not place new public-facing copy directly in `tools/build_project_html.py`. Put it in locale or project data files.

## Document Catalog

`project_data/document_catalog.json` is the registry for documentation surfaces. Update it when:

- creating a document;
- deleting a document;
- splitting or merging documents;
- changing a document's language role;
- changing whether a document is generated or source-authored;
- adding a new stable entrypoint.

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
