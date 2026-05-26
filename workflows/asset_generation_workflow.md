# Asset Generation Workflow

This workflow is the source of truth for turning the existing full character sheets into reusable transparent assets. Internal workflow documentation is English; public page copy is localized through data files.

## 1. Start From The Character Folder

Each agent must work inside one character root:

- `assets/characters/qingyou/`
- `assets/characters/arisu/`

Do not place generated assets in `assets/images/`; reusable character assets must stay inside the character root or a clearly named project-wide output folder.

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

For a lightweight QA pass before generation, build the crop review board:

```bash
python tools/build_crop_review.py
```

Open `logs/crop_review/index.html` and review only obvious failures first: clipped silhouette, cropped-out prop tips, strong neighbor bleed, or clearly off-target boxes. Do not force a full crop refactor before generation.

Before reading generated HTML pages for context, use:

```bash
python skills/project-doc-governance/scripts/read_html_doc.py knowledge/workflow.html
```

## 3. Crop Accuracy And Full-Sheet Fallback

The first crop pass is a working reference layer, not a final truth layer. Some crops may be slightly skewed, too tight, or missing context. Do not stop the whole pipeline just to perfect every crop.

When a generated asset fails because the crop is unclear:

1. Open the full source sheet in `source_sheet/` and inspect the original context.
2. Use the full sheet as a secondary reference image together with the crop.
3. If the crop is too misleading, make a one-off corrected crop and save it with a new version suffix, for example `camera-v2.png`.
4. Only edit `crop_manifest.csv` when the fix should become the new standard for future agents.
5. Log the failure and recovery in `logs/issue_memory.csv`.

This rule exists because the goal is stable asset production. Crops are useful handles, but the full sheet remains the visual authority for identity, outfit structure, and accessory placement.

## 4. Regenerate From Crops

Use each crop as a reference image. The generation target is a clean, textless, borderless asset on a flat `#ff00ff` background.

When an external API key is available, the default provider for production batches is:

- base URL: `https://yunwu.ai`
- model: `gpt-image-2`
- default reference-batch concurrency: `5`
- request route for crop references: `POST /v1/images/edits`
- request setting: `moderation=low`

Keep API keys outside the repository. Read them from a local key file or environment variable, and never print the full key in logs. Before using a key for batch production, run:

```bash
python tools/yunwu_api_smoke.py --key-file C:\Users\cyz19\Desktop\gptimg2.txt
```

Use `--generate-smoke` only when a real low-quality test image is acceptable, because it can consume credit. The `https://api.yunwu.cloud` base URL may reject keys created for `https://yunwu.ai`; trust the smoke-test result for the specific key.

Run reference-image batches with:

```bash
python tools/yunwu_generate_assets.py --key-file C:\Users\cyz19\Desktop\gptimg2.txt --asset qingyou:props:bookmark --asset arisu:props:notebook --reference-mode edit --concurrency 5 --max-attempts 2 --quality low --size 1024x1024
```

The batch script uploads each registry `source_crop` as multipart `image`, uses the full prompt sections from the prompt Markdown files, sends `moderation=low`, retries failed assets, saves chroma images, removes background locally, updates `asset_registry.csv`, and appends progress rows. Do not hard-truncate prompts; the `#ff00ff` output rule must remain intact at the end of the prompt.

Prompt notes live in:

- `assets/characters/qingyou/prompts/asset_prompts.md`
- `assets/characters/arisu/prompts/asset_prompts.md`
- `prompts/character_sheet_prompt_notes.md`

Every generation prompt must include the style layer. Compose prompts in this order:

1. Reference directive: use the visible crop as the visual reference.
2. Global style anchor from `prompts/character_sheet_prompt_notes.md`.
3. Character style anchor from the character prompt file.
4. Asset-slot subject request from the matching section, such as `props`, `clothing`, or `expressions`.
5. Composition requirements: one object or one character view, centered, complete silhouette, generous padding.
6. Negative and output constraints: no text, no labels, no frame, no unrelated objects, flat chroma-key background.

Generated pre-alpha images must be saved under:

```text
assets/characters/<character>/generated/chroma/<asset_type>/
```

Use versioned names, for example:

```text
assets/characters/qingyou/generated/chroma/props/camera-v1.png
assets/characters/arisu/generated/chroma/accessories/key-necklace-v1.png
```

## 5. Remove Chroma Background

Run:

```bash
python tools/remove_chroma_batch.py --character qingyou --asset-type props
```

Built-in image generation can produce a near-magenta background instead of exact `#ff00ff`. If the default batch remover leaves nonzero alpha in the four corners, rerun the single image through the system chroma helper with border auto-key sampling:

```bash
python C:\Users\cyz19\.codex\skills\.system\imagegen\scripts\remove_chroma_key.py --input assets/characters/<character>/generated/chroma/<asset_type>/<name>.png --out assets/characters/<character>/generated/transparent/<asset_type>/<name>.png --auto-key border --soft-matte --transparent-threshold 42 --opaque-threshold 132 --despill --force
```

The output is mirrored into:

```text
assets/characters/<character>/generated/transparent/<asset_type>/
```

If an edge is dirty, keep the attempt and log the issue in `logs/issue_memory.csv`. Put unusable but informative attempts under:

```text
assets/characters/<character>/generated/rejected/
```

## 6. Register Assets

Every asset needs a row in `logs/asset_registry.csv`.

Use these statuses:

- `planned`
- `cropped`
- `chroma-generated`
- `transparent-ready`
- `rejected`
- `needs-redraw`

The web pages can already render with missing assets. Finished transparent PNGs automatically replace crop previews during the next HTML build.

## 7. Rebuild And Validate

Run:

```bash
python tools/build_project_html.py
python tools/validate_assets.py
```

Use `--strict` only when the phase requires every transparent PNG to exist.

The default HTML build writes the Chinese root site and the English mirror under `en/`.

## 8. Preserve Learnings

Any reusable problem, fix, prompt rule, crop rule, or edge-removal note belongs in:

```text
logs/issue_memory.csv
```

This CSV is intentionally lightweight so future agents can recall known traps before repeating them.
