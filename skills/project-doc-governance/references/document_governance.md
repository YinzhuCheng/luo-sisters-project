# Document Governance Reference

## Purpose

This project uses documentation as an operational system, not as loose notes. Markdown and HTML are both documentation surfaces. Agents must be able to enter from a small number of stable files, inspect one page at a time, and follow explicit links only when needed.

## Entry Order

Use this order unless the user points to a specific file:

1. `AGENTS.md`
2. `README.md`
3. `docs/document_governance.md`
4. `docs/content_map.md`
5. `knowledge/navigation.html`
6. `knowledge/assets.html` or a linked child page

## Reading HTML

Default behavior:

- Run `scripts/read_html_doc.py` before reading raw HTML.
- Read one page or one anchor section at a time.
- Prefer `knowledge/navigation.html` for structure and `knowledge/assets.html` for path lookup.
- Treat images as placeholders.
- Ignore decorative frontend layers unless debugging layout.
- Open real images only when visual judgment is required.

Use `--structure-mode` when you need the reading route first. In that mode, the reader groups links by category and makes planned transparent outputs visible without treating them as broken. Use `--include-images` only when asset paths matter. Use image or browser tools only when the user asks for visual inspection or when layout/asset correctness is the task.

## Language Policy

- Internal maintenance documents are English.
- Public display copy is localized.
- The Chinese root site is generated from `locales/zh-CN.json` and Chinese content data.
- The English mirror is generated under `en/`.

## Ownership

- `AGENTS.md`: agent operating rules and entry map.
- `README.md`: human quick start and build instructions.
- `docs/document_governance.md`: governing principles and reading policy.
- `docs/content_map.md`: where content lives after restructuring.
- `project_data/document_catalog.json`: machine-readable document registry.
- `project_data/knowledge_base*.json`: generated knowledge-page content.
- `knowledge/assets.html`: public asset lookup surface.
- `locales/*.json`: public UI copy and localized homepage/character copy.

## Update Rules

When adding or changing documentation:

- Link it from `AGENTS.md` or `README.md`.
- Register it in `project_data/document_catalog.json`.
- Keep generated HTML out of manual editing sources.
- Rebuild generated pages after changing source data.
- Log progress and reusable pitfalls in CSV.
