# Parallel Agent Guide

The project is designed for multiple agents to work without stepping on each other.

Read `AGENTS.md`, `docs/document_governance.md`, and this guide before taking ownership of an asset scope. For HTML context, use `skills/project-doc-governance/scripts/read_html_doc.py` and follow one page at a time.

## Ownership Boundaries

One agent should own one of these scopes at a time:

- `assets/characters/qingyou/generated/transparent/standing/`
- `assets/characters/qingyou/generated/transparent/expressions/`
- `assets/characters/qingyou/generated/transparent/turnaround/`
- `assets/characters/qingyou/generated/transparent/clothing/`
- `assets/characters/qingyou/generated/transparent/accessories/`
- `assets/characters/qingyou/generated/transparent/props/`
- `assets/characters/qingyou/generated/transparent/details/`
- `assets/characters/arisu/generated/transparent/standing/`
- `assets/characters/arisu/generated/transparent/expressions/`
- `assets/characters/arisu/generated/transparent/turnaround/`
- `assets/characters/arisu/generated/transparent/clothing/`
- `assets/characters/arisu/generated/transparent/accessories/`
- `assets/characters/arisu/generated/transparent/props/`
- `assets/characters/arisu/generated/transparent/details/`

CG work is intentionally separate and should not block the first-page asset pass.

## Naming Rules

Use lowercase kebab-case and version suffixes:

```text
camera-v1.png
camera-v2.png
key-necklace-v1.png
classic-lolita-dress-v1.png
```

Do not overwrite a previous version unless the user explicitly asks for replacement.

## Logging Rules

Append to `logs/progress_updates.csv` when you:

- create or adjust crops
- generate chroma sources
- produce transparent PNGs
- reject an attempt
- change prompts or workflow files
- rebuild web pages

Append to `logs/issue_memory.csv` when you hit a reusable trap:

- identity drift
- edge color residue
- text accidentally appearing inside images
- crop too tight for long hair or lace
- asset saved into the wrong character folder
- Python command resolving to the Windows Store shim

Append to `logs/asset_registry.csv` when a planned asset changes status.

## Web Build Rules

The web layer owns:

- Chinese and English localized text
- labels
- borders
- color swatches
- layout
- responsive behavior

The generated image layer owns:

- character body and face
- outfit forms
- accessories
- props
- visual details

Do not ask the image model to generate long Chinese text for final pages.

## Handoff Checklist

Before ending a work session, leave the next agent with:

- updated CSV rows
- output paths
- prompt path or prompt section
- known issues
- whether `tools/validate_assets.py` passed
