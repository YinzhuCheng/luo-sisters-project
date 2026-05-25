# Luo Qingyou x Luo Arisu Character Project

This repository is an original anime-style character project designed for long-running Codex and multi-agent collaboration. The current system turns full character sheets into structured web pages, strict asset folders, reference-crop workflows, bilingual public pages, and reusable documentation memory.

## Quick Entry

1. Read `AGENTS.md` for agent rules.
2. Read `docs/skill_navigation.md` to choose the right repo-local skill.
3. Read `docs/document_governance.md` for documentation policy.
4. Read `docs/content_map.md` for the content hierarchy.
5. Read `harness/golden_principles.md` for the harness model.
6. Read `harness/ownership_map.json` for write boundaries.
7. Read `docs_mirror/knowledge/navigation.md` or `docs_mirror/en/knowledge/navigation.md` for structured reading paths.
8. Read `docs_mirror/knowledge/assets.md` or `docs_mirror/en/knowledge/assets.md` for asset lookup.
9. Open `index.html` for the Chinese public showcase.
10. Open `en/index.html` for the English mirror.
11. Use `skills/project-doc-governance/scripts/read_html_doc.py` before reading large raw HTML files.
12. Read `docs/browser_automation.md` before visual smoke checks.
13. Read `docs/harness_ci.md` for GitHub Actions harness runs and failure triage.

Prefer a matching repo-local skill before reading raw workflow docs or manually chaining tools.

## Build The Website

Build all public locales:

```bash
python tools/build_project_html.py
```

Build one locale:

```bash
python tools/build_project_html.py --locale zh-CN
python tools/build_project_html.py --locale en
python tools/build_html_markdown_mirror.py
```

Generated outputs:

- `index.html`
- `character_sheets/qingyou.html`
- `character_sheets/arisu.html`
- `knowledge/index.html`
- `knowledge/assets.html`
- `knowledge/characters.html`
- `knowledge/story.html`
- `knowledge/visual.html`
- `knowledge/workflow.html`
- `en/index.html`
- `en/character_sheets/qingyou.html`
- `en/character_sheets/arisu.html`
- `en/knowledge/assets.html`
- `en/knowledge/*.html`

## Low-Token HTML Reading

Prefer `docs_mirror/` for normal reading. Do not open large raw HTML files directly unless the task is layout debugging. Summarize one page or one anchor first:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/navigation.html --structure-mode
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/assets.html
python skills/project-doc-governance/scripts/read_html_doc.py character_sheets/qingyou.html --anchor workflow
```

The reader hides scripts, styles, navigation, headers, footers, SVG/canvas decoration, and image payloads. It also classifies links, checks local path existence, and summarizes asset references while keeping images as placeholders until visual inspection is needed.

## Markdown Mirrors

Generated Markdown mirrors live under `docs_mirror/` and track every project HTML page.

- `docs_mirror/index.md`
- `docs_mirror/character_sheets/*.md`
- `docs_mirror/knowledge/*.md`
- `docs_mirror/en/**/*.md`

Use mirrors as the default agent-readable layer. They are derived output, not editing sources.

## Repo-Local Skills

Use `docs/skill_navigation.md` as the entrypoint.

- `skills/project-doc-governance/`: doc reading, mirror-first navigation, and HTML audit
- `skills/character-asset-production/`: crop-to-transparent asset production and asset registration
- `skills/parallel-asset-ownership/`: multi-agent packet boundaries and handoff discipline
- `skills/harness-task-execution/`: packet execution, evidence reading, and CI triage

## Browser Automation

Browser automation is available through Python Playwright with Chromium installed.

Install or repair with the bundled runtime:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pip install -r requirements-browser.txt
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m playwright install chromium
```

Quick smoke check:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\browser_smoke_check.py index.html
```

See `docs/browser_automation.md` for the browser automation workflow.

## Data And Localization

- `locales/zh-CN.json`: Chinese public UI and page copy.
- `locales/en.json`: English public UI and page copy.
- `project_data/knowledge_base.json`: Chinese generated knowledge content.
- `project_data/knowledge_base.en.json`: English generated knowledge content.
- `characters/qingyou.json`, `characters/arisu.json`: character asset slots, palettes, layout, and paths.
- `project_data/document_catalog.json`: machine-readable documentation registry.

Keep internal maintenance docs in English. Keep public display copy in locale or data files. Do not hardcode public-facing copy in Python templates.

## Harness Control Plane

Harness engineering assets live under `harness/`.

- `harness/golden_principles.md`: high-level harness model.
- `harness/ownership_map.json`: ownership and write boundaries.
- `harness/policies/`: policy and evidence schemas.
- `harness/check_profiles/`: task-type check mappings.
- `harness/task_templates/`: task packet schema and examples.
- `harness/tasks/`: concrete executable task packets.

The harness is the machine-readable governance layer; Markdown docs explain it, but future execution should rely on harness metadata.

## Harness CI

GitHub Actions runs the harness delivery loop through:

- `.github/workflows/harness-docs.yml`
- `.github/workflows/harness-pages.yml`
- `.github/workflows/harness-assets.yml`
- `.github/workflows/harness-maintenance.yml`

Use `docs/harness_ci.md` when a run fails or warns. Start with the uploaded `report.json`, then `summary.md`, then the packet and check profile referenced by the report.
Maintenance runs also refresh `harness/quality_score.json` and emit `score.json` inside the uploaded run bundle.

## Harness CLI

The first harness execution entrypoint is:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py preflight harness\task_templates\task_packet.example.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py verify harness\task_templates\task_packet.example.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py bundle harness\task_templates\task_packet.example.json
```

Harness run artifacts write to `logs/harness_runs/<timestamp>-<task-id>/`.

For one-step local execution, use:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\run_harness_task.py harness\tasks\site-smoke-check.json
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\harness_cli.py score
```

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
- `poses`
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

- `index.html` is a lightweight public showcase, not the complete long-form knowledge layer.
- `knowledge/*.html` and `en/knowledge/*.html` are generated structured knowledge pages.
- `knowledge/assets.html` and `en/knowledge/assets.html` are the unified asset lookup pages.
- `docs/content_map.md` explains where old and new content live.

## Project Memory

All agents should maintain CSV logs:

- `logs/progress_updates.csv`: work progress.
- `logs/asset_registry.csv`: asset status registry.
- `logs/issue_memory.csv`: reusable pitfalls and mitigations.

These logs are future skill material.
