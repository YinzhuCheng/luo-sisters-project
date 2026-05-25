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
- `assets/characters/<character>/prompts/asset_prompts.md`
- `assets/characters/<character>/workflow/crop_manifest.csv`
- `logs/asset_registry.csv`
- `workflows/asset_generation_workflow.md`

## Production Route

1. Start from `source_sheet/`.
2. Crop or inspect the needed reference.
3. Generate a textless asset on flat `#ff00ff`.
4. Save chroma output under `generated/chroma/<asset_type>/`.
5. Remove chroma and save transparent output under `generated/transparent/<asset_type>/`.
6. Move unstable attempts to `generated/rejected/`.
7. Register the result in `logs/asset_registry.csv`.
8. Log meaningful progress and reusable issues.

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
