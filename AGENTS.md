# AGENTS.md | Luo Qingyou x Luo Arisu Project Navigation

This is the primary entrypoint for Codex and other automated agents. Read this file first, then follow the linked hierarchy instead of opening large HTML pages directly.

## Project Goal

Build a sustainable original anime-style character project:

- Older sister: Luo Qingyou, Chinese-inspired classic Lolita, planner, recorder, gentle sister.
- Younger sister: Luo Arisu, JK Lolita, Alice motif, explorer, doorway to dreams.
- Surface story: the sisters prepare a Rabbit Hole Tea Party.
- Core theme: order and disorder in daily life, anxiety management, and the search for meaning in the AIGC era.

## Required Reading Order

1. `AGENTS.md`
2. `README.md`
3. `docs/document_governance.md`
4. `docs/content_map.md`
5. `knowledge/navigation.html`
6. `knowledge/assets.html` or a linked child page
7. `docs/browser_automation.md` before browser-based visual QA

For HTML, use the low-token reader first:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/navigation.html --structure-mode
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/assets.html
```

Read one HTML page or anchor at a time. Treat images as placeholders until visual inspection is needed.

## Key Files

- `README.md`: human quick start and build commands.
- `docs/document_governance.md`: documentation governance law, language policy, and reading rules.
- `docs/content_map.md`: where content lives after the HTML-sheet restructure.
- `project_data/document_catalog.json`: machine-readable document registry.
- `skills/project-doc-governance/`: project skill for low-token HTML reading and doc governance.
- `tools/build_project_html.py`: generates the Chinese root site and English `en/` mirror.
- `locales/zh-CN.json`, `locales/en.json`: public UI and page copy.
- `project_data/knowledge_base.json`, `project_data/knowledge_base.en.json`: generated knowledge-page content.
- `characters/qingyou.json`, `characters/arisu.json`: character asset slots, palettes, layout, and paths.
- `assets/characters/qingyou/`, `assets/characters/arisu/`: strictly separated character asset roots.
- `knowledge/assets.html`: unified public asset index.
- `docs/browser_automation.md`: Playwright setup and smoke-check entrypoint.
- `workflows/asset_generation_workflow.md`: crop-to-transparent-asset workflow.
- `workflows/agent_parallel_guide.md`: parallel-agent ownership rules.
- `logs/progress_updates.csv`, `logs/asset_registry.csv`, `logs/issue_memory.csv`: project memory.

## Build Commands

Build both public locales:

```bash
python tools/build_project_html.py
```

Build one locale:

```bash
python tools/build_project_html.py --locale zh-CN
python tools/build_project_html.py --locale en
```

If Windows resolves `python` to the Microsoft Store shim, use the bundled runtime:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\build_project_html.py
```

Validate assets:

```bash
python tools/validate_assets.py
```

Validate the project skill:

```bash
python C:\Users\cyz19\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/project-doc-governance
```

Run a browser smoke check:

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\browser_smoke_check.py index.html
```

## Governance Rules

- Treat `.md` and `.html` as documentation.
- Keep internal maintenance documents in English.
- Keep public page copy in locale or data files, not hardcoded inside Python templates.
- Generated HTML is output, not the long-term editing source.
- Every new document must be reachable from `AGENTS.md` or `README.md`.
- Every new, moved, split, or merged document must be registered in `project_data/document_catalog.json`.
- When content looks missing, check `knowledge/navigation.html`, `knowledge/assets.html`, `project_data/knowledge_base*.json`, `logs/asset_registry.csv`, then `docs/content_map.md` before rewriting.

## Image Asset Rules

- New character assets must live under `assets/characters/<character>/`.
- Qingyou and Arisu folders must remain strictly isolated for parallel-agent work.
- Generation route: crop from full sheet -> regenerate clean `#ff00ff` chroma image -> remove background locally -> save transparent PNG.
- Crops are working handles, not the visual truth. If a crop is skewed, tight, or missing context, inspect the full `source_sheet/` image before changing manifests.
- Planned assets can exist without crops; track them in `characters/*.json` and `logs/asset_registry.csv` until reference crops are created.
- Finished transparent PNGs go to `generated/transparent/<asset_type>/`.
- Failed or unstable attempts go to `generated/rejected/`.
- Final Chinese and English labels belong to the web layer, not image generation.

## Logging Rules

- Append `logs/progress_updates.csv` for meaningful work progress.
- Update or append `logs/asset_registry.csv` when an asset changes status.
- Append `logs/issue_memory.csv` for reusable traps, causes, and mitigations.
- CSV logs are source material for future skills; do not leave reusable knowledge only in chat.

## Recommended Next Tasks

1. Use the document governance skill for HTML structure reads and asset-path inspection.
2. Keep `knowledge/assets.html` and `logs/asset_registry.csv` synchronized with character JSON.
3. Generate transparent character assets by character and asset type.
4. Extract stable rules from `logs/issue_memory.csv` into reusable skills when patterns repeat.
