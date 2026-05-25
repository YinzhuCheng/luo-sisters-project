# Asset Generation Workflow

This workflow is the source of truth for turning the existing full character sheets into reusable transparent assets.

## 1. Start From The Character Folder

Each agent must work inside one character root:

- `assets/characters/qingyou/`
- `assets/characters/arisu/`

Do not place generated assets in `assets/images/` unless the asset is a legacy whole-sheet archive or a final project-wide visual.

## 2. Crop Reference Images

Reference crops come from the copied source sheets:

- `assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png`
- `assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png`

Run:

```bash
python tools/crop_from_sheet.py --character all --force
```

On this Windows workspace, the bundled runtime is available at:

```text
C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

Each crop is controlled by:

- `assets/characters/qingyou/workflow/crop_manifest.csv`
- `assets/characters/arisu/workflow/crop_manifest.csv`

If you adjust crop coordinates, update the manifest and append a row to `logs/progress_updates.csv`.

## 3. Regenerate From Crops

Use each crop as a reference image. The generation target is a clean, textless, borderless asset on a flat `#ff00ff` background.

Prompt notes live in:

- `assets/characters/qingyou/prompts/asset_prompts.md`
- `assets/characters/arisu/prompts/asset_prompts.md`

Generated pre-alpha images must be saved under:

```text
assets/characters/<character>/generated/chroma/<asset_type>/
```

Use versioned names, for example:

```text
assets/characters/qingyou/generated/chroma/props/camera-v1.png
assets/characters/arisu/generated/chroma/accessories/key-necklace-v1.png
```

## 4. Remove Chroma Background

Run:

```bash
python tools/remove_chroma_batch.py --character qingyou --asset-type props
```

The output is mirrored into:

```text
assets/characters/<character>/generated/transparent/<asset_type>/
```

If an edge is dirty, keep the attempt and log the issue in `logs/issue_memory.csv`. Put unusable but informative attempts under:

```text
assets/characters/<character>/generated/rejected/
```

## 5. Register Assets

Every asset needs a row in `logs/asset_registry.csv`.

Use these statuses:

- `planned`
- `cropped`
- `chroma-generated`
- `transparent-ready`
- `rejected`
- `needs-redraw`

The web pages can already render with missing assets. Finished transparent PNGs automatically replace crop previews during the next HTML build.

## 6. Rebuild And Validate

Run:

```bash
python tools/build_project_html.py
python tools/validate_assets.py
```

Use `--strict` only when the phase requires every transparent PNG to exist.

## 7. Preserve Learnings

Any reusable problem, fix, prompt rule, crop rule, or edge-removal note belongs in:

```text
logs/issue_memory.csv
```

This CSV is intentionally lightweight so future agents can recall known traps before repeating them.
