# Luo Qingyou x Luo Arisu

Source HTML: `en/index.html`

## Content
Character Bible · HTML Sheet System | 0.5-doc-governance
# Luo Qingyou x Luo Arisu
Build the website as a stable display window first, then regenerate clothing, accessories, expressions, and props as transparent reusable assets.
[image placeholder: alt="Luo Qingyou" src="../../assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png"]
Luo Qingyou
[image placeholder: alt="Luo Arisu" src="../../assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png"]
Luo Arisu
Stage 01
## Current Goal
This stage separates the original full-sheet images into structured web pages and an asset pipeline. HTML/CSS owns text, frames, palettes, and labels; generated images own characters, outfits, accessories, and props.
### Surface
The sisters prepare a Rabbit Hole Tea Party through outfits, journals, photography, old libraries, invitations, and small props.
### Character
Qingyou protects dreams through order; Arisu searches for dreams through exploration. Their complementarity becomes conflict and then co-creation.
### Core
AIGC gradually amplifies anxieties about replacement, perfect dreams, and outsourced choices. The ending returns tools to their proper place while people keep direction, judgment, and relationships.
Character Sheets
## Character Sheets
The page uses reference crops and stable placeholders first. Finished transparent PNG assets will replace their slots automatically.
[image placeholder: alt="Luo Qingyou" src="../../assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png"]
[image placeholder: alt="Luo Arisu" src="../../assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png"]
Workflow
## Web And Asset Pipeline
- Build the index page and two HTML character sheets first.
- Crop references from the existing full character sheets into strict character folders.
- Regenerate textless, borderless, solid-background versions from those crops.
- Remove the chroma key locally to produce transparent PNG assets and log them in CSV.
- Replace page placeholders with transparent assets while the web layer keeps final typography and labels.
Content Map
## Content Hierarchy
The current index is a lightweight display hub. Long-form content now lives across structured pages, character data, workflows, and the asset registry.
### 0 | Current Showcase
Pages for browsing and presentation.
- [Index](index.md) Current navigation and display window
- [Qingyou HTML Sheet](character_sheets/qingyou.md) Journal-style character sheet
- [Arisu HTML Sheet](character_sheets/arisu.md) Blue Alice character sheet
- [Structured Knowledge Base](knowledge/index.md) Structured reading and planning hub
- [Asset Index](knowledge/assets.md) Character roots, slots, prompts, and outputs
### 1 | Structured Knowledge
Task-based knowledge pages and the shared asset index for structured reading.
- [Knowledge Index](knowledge/index.md) Entry to structured project pages
- [Navigation And Reading Paths](knowledge/navigation.md) What to read first and where to go next
- [Asset Index](knowledge/assets.md) All characters, asset types, prompts, and planned outputs
- [Characters](knowledge/characters.md) Eight-layer character notes and sister relationship
- [Story](knowledge/story.md) Chapter flow, AIGC rhythm, and scene hooks
- [Visual Prompts](knowledge/visual.md) Art direction, prompt groups, and duo key visual
- [Workflow And Assets](knowledge/workflow.md) Production flow, asset list, checklist, and next steps
### 2 | Data And Locales
Generated pages use separated data and localized copy.
- [Chinese Locale](../../locales/zh-CN.json) Default web copy
- [English Locale](../../locales/en.json) Future language switching
- [Qingyou Config](../../characters/qingyou.json) Palette, layout, asset slots
- [Arisu Config](../../characters/arisu.json) Palette, layout, asset slots
- [Knowledge Data](../../project_data/knowledge_base.json) Structured page summaries and workflow copy
- [Earlier Overview Data](../../project_data/luo_sisters_overview.json) Retained structured content
### 3 | Production Memory
Workflow, parallel-agent rules, logs, and reusable issue memory.
- [Asset Workflow](../../workflows/asset_generation_workflow.md) Includes full-sheet fallback rule
- [Parallel Agent Guide](../../workflows/agent_parallel_guide.md) Ownership and handoff rules
- [Content Map](../../docs/content_map.md) Where content moved
- [Progress CSV](../../logs/progress_updates.csv) Work log
- [Issue Memory CSV](../../logs/issue_memory.csv) Pitfalls and mitigations
- [Asset Registry CSV](../../logs/asset_registry.csv) Asset statuses
Story
## Story Outline
The sisters prepare a Rabbit Hole Tea Party together.The surface is a sweet daily-life tea party project. The middle layer is order versus disorder. The deep layer reflects on value, companionship, advice, and generated content in the AIGC era.
1. Act 1: Leave a Page for the DreamArisu proposes a tea party for people who get lost. Qingyou writes it into her journal.
1. Act 2: The Dream Becomes FasterClassmates generate posters and plans with AI. Qingyou feels displaced, while Arisu is drawn to perfect Alice imagery.
1. Act 3: Even Getting Lost Is ScheduledQingyou over-optimizes the invitation and process. Arisu feels her strange sentences have been flattened.
1. Act 4: Choose the Door AgainBoth admit their fears and reassign AI to repetitive work while they keep direction and relationships.
1. Finale: An Imperfect Tea PartyRain, lateness, soft-focus photos, and blank journal space make the day truly theirs.
HTML / CSS / asset workflow generated from structured data. Public pages are Chinese-first with an English mirror and locale separation.

## Page Links
- `html | ok | English Qingyou character sheet mirror` Luo Qingyou: [character_sheets/qingyou.md](character_sheets/qingyou.md)
- `html | ok | English Arisu character sheet mirror` Luo Arisu: [character_sheets/arisu.md](character_sheets/arisu.md)
- `html | ok | English structured knowledge index` Knowledge: [knowledge/index.md](knowledge/index.md)
- `html | ok | English asset index` Assets: [knowledge/assets.md](knowledge/assets.md)
- `html | ok | English Qingyou character sheet mirror` Classic Lolita | Planner | Archivist | Gentle Older Sister Luo QingyouLuo Qingyou A person who protects dreams through order. Sage classic LolitaJournal and vintage cameraCloud collar, frog buttons, laceOld street, tea party, window light Open Sheet: [character_sheets/qingyou.md](character_sheets/qingyou.md)
- `html | ok | English Arisu character sheet mirror` JK Lolita | Alice Motif | Explorer | Doorway to Dreams Luo ArisuLuo Arisu A person who searches for dreams through disorder. Blue-white JK LolitaKey necklace, rabbit charm, pocket watchDaisy, old books, school bagSchool hallway, old library, secret door Open Sheet: [character_sheets/arisu.md](character_sheets/arisu.md)
- `html | ok | English public showcase mirror` Index: [index.md](index.md)
- `html | ok | English Qingyou character sheet mirror` Qingyou HTML Sheet: [character_sheets/qingyou.md](character_sheets/qingyou.md)
- `html | ok | English Arisu character sheet mirror` Arisu HTML Sheet: [character_sheets/arisu.md](character_sheets/arisu.md)
- `html | ok | English structured knowledge index` Structured Knowledge Base: [knowledge/index.md](knowledge/index.md)
- `html | ok | English asset index` Asset Index: [knowledge/assets.md](knowledge/assets.md)
- `html | ok | English structured knowledge index` Knowledge Index: [knowledge/index.md](knowledge/index.md)
- `html | ok | English structured navigation page` Navigation And Reading Paths: [knowledge/navigation.md](knowledge/navigation.md)
- `html | ok | English character knowledge page` Characters: [knowledge/characters.md](knowledge/characters.md)
- `html | ok | English story knowledge page` Story: [knowledge/story.md](knowledge/story.md)
- `html | ok | English visual knowledge page` Visual Prompts: [knowledge/visual.md](knowledge/visual.md)
- `html | ok | English workflow knowledge page` Workflow And Assets: [knowledge/workflow.md](knowledge/workflow.md)
- `json | ok` Chinese Locale: [../../locales/zh-CN.json](../../locales/zh-CN.json)
- `json | ok` English Locale: [../../locales/en.json](../../locales/en.json)
- `json | ok` Qingyou Config: [../../characters/qingyou.json](../../characters/qingyou.json)
- `json | ok` Arisu Config: [../../characters/arisu.json](../../characters/arisu.json)
- `json | ok` Knowledge Data: [../../project_data/knowledge_base.json](../../project_data/knowledge_base.json)
- `json | ok` Earlier Overview Data: [../../project_data/luo_sisters_overview.json](../../project_data/luo_sisters_overview.json)
- `markdown | ok | asset production workflow` Asset Workflow: [../../workflows/asset_generation_workflow.md](../../workflows/asset_generation_workflow.md)
- `markdown | ok | parallel-agent ownership guide` Parallel Agent Guide: [../../workflows/agent_parallel_guide.md](../../workflows/agent_parallel_guide.md)
- `markdown | ok | content hierarchy map` Content Map: [../../docs/content_map.md](../../docs/content_map.md)
- `csv | ok` Progress CSV: [../../logs/progress_updates.csv](../../logs/progress_updates.csv)
- `csv | ok` Issue Memory CSV: [../../logs/issue_memory.csv](../../logs/issue_memory.csv)
- `csv | ok` Asset Registry CSV: [../../logs/asset_registry.csv](../../logs/asset_registry.csv)

## Page Anchors
- `viewport`
- `overview`
- `characters`
- `workflow`
- `content-map`
- `story`

## Resource References
- `asset | ok` ../../assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png alt="Luo Qingyou"
- `asset | ok` ../../assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png alt="Luo Arisu"
