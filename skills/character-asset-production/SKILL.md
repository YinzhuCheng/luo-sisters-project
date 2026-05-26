---
name: character-asset-production
description: Produce Luo Sisters character assets from source sheet to transparent PNG. Use when Codex needs to crop references, regenerate textless chroma assets, remove `#ff00ff` backgrounds, register asset status, apply full-sheet fallback when crops are weak, or validate asset outputs before handoff.
---

# Character Asset Production

Use this skill for actual character asset work inside `assets/characters/qingyou/` or `assets/characters/arisu/`.

## Workflow

1. Stay inside one character root and one asset-type scope at a time.
2. Check `characters/<character>.json`, `logs/asset_registry.csv`, `prompts/character_sheet_prompt_notes.md`, and the character prompt file before generating or revising outputs.
3. Create or inspect crops from `source_sheet/`, then treat them as working handles rather than final truth.
4. Generate a clean, textless, borderless asset on flat `#ff00ff`.
5. Remove chroma locally, keep transparent outputs under the correct `generated/transparent/<asset_type>/` subtree, and keep failed attempts under `generated/rejected/`.
6. Update `logs/asset_registry.csv` and `logs/progress_updates.csv`, then run validation before handoff.

## Core Commands

```bash
python tools/build_crop_review.py
python tools/crop_from_sheet.py --character all --force
python tools/yunwu_api_smoke.py --key-file C:\Users\cyz19\Desktop\gptimg2.txt
python tools/yunwu_generate_assets.py --key-file C:\Users\cyz19\Desktop\gptimg2.txt --asset qingyou:props:bookmark --reference-mode edit --concurrency 5 --max-attempts 2 --quality low --size 1024x1024
python tools/remove_chroma_batch.py --character qingyou --asset-type props
python tools/build_project_html.py
python tools/validate_assets.py
```

Use the bundled runtime when `python` resolves to the Windows Store shim.

## Required Rules

- Keep work inside `assets/characters/<character>/`.
- Build generation prompts from the reference crop, global style anchor, character style anchor, asset-slot request, composition constraints, negative constraints, and chroma-key output rule.
- When an external key is available, default to `https://yunwu.ai` + `gpt-image-2` edit batches, upload the registry `source_crop`, set `moderation=low`, and keep batch concurrency at `5` unless rate limits appear.
- Do not hard-truncate generation prompts; the final chroma-key output rule must stay intact.
- Use versioned lowercase kebab-case names such as `camera-v1.png`.
- Keep planned assets registered even before crops or outputs exist.
- Use `tools/build_crop_review.py` for a lightweight pre-generation QA pass and fix only obvious failures first.
- If a crop is skewed, tight, or missing context, inspect the full `source_sheet/` image before changing manifests.
- Do not delete informative failed attempts; move them to `generated/rejected/`.
- Let the web layer own final labels, borders, and long text.

## Handoff

Leave:

- output paths
- prompt path or section
- current asset status in `logs/asset_registry.csv`
- progress notes in `logs/progress_updates.csv`
- reusable traps in `logs/issue_memory.csv`
- whether `tools/validate_assets.py` passed

## Switch To Another Skill When

- the task becomes doc reading, catalog maintenance, or HTML audit -> `project-doc-governance`
- the task becomes multi-agent scope splitting or handoff boundary work -> `parallel-asset-ownership`
- the task becomes packet execution, CI triage, or harness evidence work -> `harness-task-execution`

## When More Detail Is Needed

Read `references/asset_production.md` for the full crop-to-transparent workflow, logging expectations, and failure recovery rules.
