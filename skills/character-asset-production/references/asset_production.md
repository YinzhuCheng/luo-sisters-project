# Character Asset Production Reference

## Use This Skill For

- reference crop generation or inspection
- chroma-to-transparent asset production
- asset registry updates
- prompt lookup by character
- full-sheet fallback when a crop is misleading
- asset validation before handoff

## Working Surface

Stay inside one character root:

- `assets/characters/qingyou/`
- `assets/characters/arisu/`

Use one asset type at a time when possible:

- `standing`
- `expressions`
- `poses`
- `turnaround`
- `clothing`
- `accessories`
- `props`
- `details`
- `cg`

## Files To Read First

- `characters/<character>.json`
- `prompts/character_sheet_prompt_notes.md`
- `assets/characters/<character>/prompts/asset_prompts.md`
- `assets/characters/<character>/workflow/crop_manifest.csv`
- `logs/asset_registry.csv`
- `workflows/asset_generation_workflow.md`
- `tools/build_crop_review.py`

## Prompt Composition

Every generation prompt should include the same style layer before asset-specific instructions:

1. reference crop directive
2. global style anchor from `prompts/character_sheet_prompt_notes.md`
3. character style anchor from `assets/characters/<character>/prompts/asset_prompts.md`
4. asset-slot subject request from the relevant section
5. composition and padding requirements
6. negative constraints and flat chroma-key output rule

Do not rely on a bare phrase such as "anime prop design" for production batches; it is too weak for multi-image consistency.

## Production Route

1. Start from `source_sheet/`.
2. Run `python tools/build_crop_review.py` for a lightweight QA pass when crop quality is uncertain.
3. Crop or inspect the needed reference.
4. Generate a textless asset on flat `#ff00ff`. When using the external provider, use `https://yunwu.ai`, model `gpt-image-2`, `/v1/images/edits`, uploaded crop references, `moderation=low`, and default concurrency `5` unless the task packet says otherwise.
5. Save chroma output under `generated/chroma/<asset_type>/`.
6. Remove chroma and save transparent output under `generated/transparent/<asset_type>/`.
7. Move unstable attempts to `generated/rejected/`.
8. Register the result in `logs/asset_registry.csv`.
9. Log meaningful progress and reusable issues.

Run `python tools/yunwu_api_smoke.py --key-file <local-key-file>` before a new external key is used for batch production. Add `--generate-smoke` only when spending one low-quality test generation is acceptable.

Run `python tools/yunwu_generate_assets.py --key-file <local-key-file> --asset <character>:<type>:<name> --reference-mode edit --concurrency 5 --max-attempts 2` for registered assets. The script reads the registry crop path and prompt sections, uploads the crop, saves chroma and transparent outputs, and updates project logs.

## Full-Sheet Fallback

The full source sheet is the visual authority. If a crop is too tight, skewed, or context-poor:

1. open the full sheet
2. compare outfit structure, accessory placement, and identity cues
3. make a one-off corrected crop with a new version only if needed
4. update the crop manifest only when the corrected crop should become standard

## Validation

Run:

```bash
python tools/validate_assets.py
```

Use `tools/build_project_html.py` when the updated asset should appear in the generated site.

## Logging Expectations

- `logs/progress_updates.csv`: progress and outputs
- `logs/asset_registry.csv`: status and path changes
- `logs/issue_memory.csv`: recurring traps, residue, drift, and crop recovery notes
