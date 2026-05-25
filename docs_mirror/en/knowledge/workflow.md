# Production Rules And Asset Planning | Luo Sisters Knowledge Base

Source HTML: `en/knowledge/workflow.html`

## Content
Knowledge 05
# Production Rules And Asset Planning
Japanese anime character-project production flow, asset list, unified checklist, and next-step suggestions.
Production Workflow
## Anime Character Project Production Flow
Move through concept, line exploration, standing art, reference sheet, key art, and application assets.
| Stage | Output | Check |
| --- | --- | --- |
| 0. Character Bible | Name, signature line, theme role, relationships, fixed identity marks. | One sentence explains who she is; three memory points stay stable. |
| 1. Moodboard | Outfit, hair, palette, material, props, scene references. | Qingyou leans sage-classic-tea; Arisu leans blue-school-Alice. |
| 2. Silhouettes | 3-6 small silhouettes per character. | They remain distinct when detail is hidden. |
| 3. Line Exploration | Hair, skirt, collar, cuffs, socks, shoes, bags. | Outfit layers and accessory positions are clear. |
| 4. Color Roughs | Three palette and lighting tests. | Main, secondary, and accent colors have clear jobs. |
| 5. Standard Standing | Full-body front standing art. | Usable as the parent image for later work. |
| 6. Turnaround | Front, side, back, with key structure notes. | Skirt, hair ornaments, straps, socks, shoes, and back bow are complete. |
| 7. Expressions | 8-12 expressions per character. | Brows, eyes, mouth, head angle, and gesture visibly differ. |
| 8. Pose Sheet | Standing, sitting, photographing, journaling, door-looking, invitation-giving. | Actions serve character, not just beauty. |
| 9. Outfit Variants | Standard, casual, tea-party, rainy-day, winter, light campus outfits. | Core identity marks survive the outfit change. |
| 10. Props | Camera, journal, key, pocket-watch bag, invitation, tea cup, school bag. | Each prop can tell story on its own. |
| 11. Key Art | Two solo key arts each and one or two duo key visuals. | Key art expresses theme, relationship, and growth. |
| 12. Application Assets | Avatars, chibi art, stickers, banners, Live2D rough splits. | Used for promotion and iteration. |
Asset List
## Unified Asset Scope
These items now live in character config, the asset index page, and asset_registry.csv instead of a legacy summary block.
### Luo Qingyou Asset List
Standard standing art, turnaround, expressions, photographing/journaling/serving tea/umbrella/adjusting bow poses, old camera, sage journal, tea cup, dried flower bookmark, spare clips, old street tea-shop light, rainy plan blank.
### Luo Arisu Asset List
Standard standing art, turnaround, curious/surprised/dreamy/shy/hurt/brave expressions, door-looking/key-holding/invitation-writing/charm-swinging/threshold poses, key necklace, pocket-watch bag, rabbit charm, old book, music box, blue ink, corridor door, before-tea-cools scene.
Unified Checklist
## Unified Checklist
Reuse these rules during generation, filing, and web linking.
- When Qingyou changes outfits, preserve sage green, journal or camera, and Chinese-inspired structure cues.
- When Arisu changes outfits, preserve blue-white, key or rabbit, and campus/Alice cues.
- Every image should answer: does this make the character clearer?
- Every prop needs narrative function: relationship, personality, or theme.
- Prefer key art that captures an event over pure standing display.
- If a crop is skewed, tight, or unclear, consult the full source_sheet before editing crop_manifest.
Next Step
## Next-Step Suggestions
Standardize references before generation and manual correction.
### 1. Fix Character Cards
Confirm age, height, birthday, school or club, family relation, speech style, and common props.
### 2. Make First Turnarounds
Start with line art or low-color roughs, inspect silhouette and structure, then add material detail.
### 3. Choose First Duo Key Visual
Start with Door And Journal: Arisu finds the door, Qingyou records and prepares the path back.
Related Files
## Related Production Files
Knowledge pages explain structure; production still follows workflows, scripts, and CSV logs.
- [Asset Index](assets.md) Single entry for character roots, crops, prompts, and planned outputs
- [Asset Generation Workflow](../../../workflows/asset_generation_workflow.md) Crop-to-transparent-asset process
- [Parallel Agent Guide](../../../workflows/agent_parallel_guide.md) Strict character and asset-type ownership
- [Asset Registry CSV](../../../logs/asset_registry.csv) Asset source, prompt, output, and status
- [Issue Memory CSV](../../../logs/issue_memory.csv) Reusable mitigation rules

## Page Links
- `html | ok | English asset index` Asset Index: [assets.md](assets.md)
- `markdown | ok | asset production workflow` Asset Generation Workflow: [../../../workflows/asset_generation_workflow.md](../../../workflows/asset_generation_workflow.md)
- `markdown | ok | parallel-agent ownership guide` Parallel Agent Guide: [../../../workflows/agent_parallel_guide.md](../../../workflows/agent_parallel_guide.md)
- `csv | ok` Asset Registry CSV: [../../../logs/asset_registry.csv](../../../logs/asset_registry.csv)
- `csv | ok` Issue Memory CSV: [../../../logs/issue_memory.csv](../../../logs/issue_memory.csv)

## Page Anchors
- `viewport`
- `production-flow`
- `asset-list`
- `checklist`
- `next`
- `related-workflows`

## Resource References
(none)
