# Luo Arisu Asset Prompts

These prompts are project-bound working notes. The public pages are locale-driven with a Chinese root site and an English mirror; prompts may use English for generation stability.

## Shared Rules

- Use the crop from `assets/characters/arisu/crops/` as the visual reference.
- Regenerate the subject as a clean reusable asset, not a full character sheet.
- No Chinese text, no labels, no decorative frame, no watermark.
- Use a perfectly flat solid `#ff00ff` chroma-key background for local background removal.
- Keep generous padding around long hair, ribbon, key, rabbit charm, and skirt edges.
- Preserve identity: blue-white JK Lolita, Alice motif, long dark hair, daisy hair ornament, gentle curious expression.

## Shared Style Anchor

Use this block in every Arisu generation prompt before the asset-specific section:

```text
Polished 2D Japanese anime character-design asset, clean confident lineart, delicate hand-painted watercolor texture, soft cel shading, warm diffuse highlights, crisp readable silhouette, source-sheet-consistent proportions, high detail without photorealism, gentle storybook-lolita mood, refined textile and metal details, no 3D render, no toy-catalog plastic, no heavy oil-paint texture, no thick western cartoon outline, no chibi deformation unless requested.
```

## Arisu Character Style Anchor

Use this block in every Arisu generation prompt after the shared style anchor:

```text
Luo Arisu style anchor: blue-white JK Lolita with Alice motif, clear porcelain white, royal and misty blue, shell beige, small cocoa accents, and clean ink details; curious younger-sister presence; long dark hair; daisy hair ornament; blue ribbons, key necklace, rabbit charm, pocket-watch motifs, lace socks, mary jane shoes, school-corridor-to-Wonderland atmosphere. Keep her line weight, face language, ribbon rendering, daisy/key motif density, and soft youthful proportions consistent with the source sheet.
```

## standard-full

Use case: stylized-concept  
Asset type: transparent character standing asset  
Primary request: Luo Arisu full-body standard standing pose, regenerated from the reference crop.  
Subject: blue-white JK Lolita girl, white blouse, blue pinafore dress, ribbon tie, daisy hair accessory, key necklace, rabbit charm or pocket watch motif, white socks, mary jane shoes.  
Style/medium: Japanese anime character design, clean lineart, soft cel shading, readable outfit construction.  
Composition/framing: full body centered, feet visible, neutral standing pose, generous padding.  
Constraints: no text, no labels, no sheet layout, no frame, no cast shadow, flat `#ff00ff` background.

## expressions

Use case: stylized-concept  
Asset type: transparent expression bust assets  
Primary request: regenerate one Luo Arisu bust expression from the selected reference crop.  
Subject: same face, long dark hair, daisy hair ornament, white blouse, blue jumper dress or red ribbon visible.  
Expression requirements: every expression must visibly differ through eyes, brows, mouth, head angle, hand gesture, or shoulder posture.  
Style/medium: Japanese anime expression reference, clean lineart, soft cel shading.  
Composition/framing: bust or half-body, centered, enough hair padding for cutout.  
Constraints: no text, no label, no frame, no shadow, flat `#ff00ff` background.

## poses

Use case: stylized-concept  
Asset type: transparent full-body pose asset  
Primary request: regenerate one Luo Arisu action pose that preserves her blue-white Alice identity and curious exploratory mood.  
Pose options: looking at a door, pinching the key, writing an invitation, swinging the bag charm, stepping into a threshold.  
Composition/framing: full body, centered, enough skirt and hair padding for cutout.  
Constraints: no text, no frame, no extra scene furniture beyond the chosen action cue, flat `#ff00ff` background.

## turnaround

Use case: stylized-concept  
Asset type: transparent turnaround view  
Primary request: regenerate the selected Luo Arisu front, side, or back view as a single transparent asset.  
Subject: blue-white JK Lolita outfit, white blouse, blue pinafore skirt, ribbon tie, key necklace, daisy hairpin, long dark hair, consistent socks and shoes.  
Style/medium: production-ready anime character reference, clean lineart and flat-soft color.  
Composition/framing: one view only, full body, centered, feet visible.  
Constraints: no labels, no guide boxes, no text, no frame, flat `#ff00ff` background.

## clothing

Use case: stylized-concept  
Asset type: transparent clothing component  
Primary request: isolate and regenerate the selected Arisu clothing component from the crop.  
Subject: blue-white JK Lolita dress, blue pinafore, daily cardigan, ribbon tie, soft pleated skirt, lace socks.  
Composition/framing: single clothing component or clean outfit fragment, centered with padding.  
Constraints: no mannequin unless necessary for readability, no text, no label, no frame, flat `#ff00ff` background.

## accessories

Use case: stylized-concept  
Asset type: transparent wearable accessory  
Primary request: regenerate the selected Arisu accessory from the crop as an individual reusable asset.  
Subject: key necklace, daisy hairpin, ribbon tie, small blue bow, Alice-inspired wearable details.  
Composition/framing: single accessory centered, readable silhouette, enough padding.  
Constraints: no text, no labels, no frame, no shadow, flat `#ff00ff` background.

## props

Use case: stylized-concept  
Asset type: transparent prop asset  
Primary request: regenerate the selected Arisu prop from the crop as a clean item asset.  
Subject options: key, pocket watch, rabbit charm, notebook, school bag, old storybook.  
Style/medium: anime prop design, clean lineart, soft color, readable material details.  
Composition/framing: one object only, centered, generous padding.  
Constraints: no text, no label, no frame, no shadow, flat `#ff00ff` background.

## details

Use case: stylized-concept  
Asset type: transparent detail asset  
Primary request: regenerate the selected Arisu design detail from the crop.  
Subject: braid detail, skirt pleat, sock and shoe, daisy motif, blue ribbon edge.  
Composition/framing: close-up component, centered, readable edges for cutout.  
Constraints: no text, no label, no frame, flat `#ff00ff` background.

## cg

Use case: illustration-story  
Asset type: future key visual reference  
Primary request: Luo Arisu in a quiet school corridor facing a softly glowing ordinary door, or writing a strange tea party invitation before the tea cools.  
Constraints: CG assets are not first-stage blockers; keep prompt drafts here until the sheet slots are stable.
