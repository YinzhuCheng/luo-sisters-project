# Luo Qingyou Asset Prompts

These prompts are project-bound working notes. The public pages are locale-driven with a Chinese root site and an English mirror; prompts may use English for generation stability.

## Shared Rules

- Use the crop from `assets/characters/qingyou/crops/` as the visual reference.
- Regenerate the subject as a clean reusable asset, not a full character sheet.
- No Chinese text, no labels, no decorative frame, no watermark.
- Use a perfectly flat solid `#ff00ff` chroma-key background for local background removal.
- Keep generous padding around hair, lace, skirt, and accessories.
- Preserve identity: long dark hair, sage green classic Lolita, warm older-sister expression, plum or gold-green hair ornament.

## Shared Style Anchor

Use this block in every Qingyou generation prompt before the asset-specific section:

```text
Polished 2D Japanese anime character-design asset, clean confident lineart, delicate hand-painted watercolor texture, soft cel shading, warm diffuse highlights, crisp readable silhouette, source-sheet-consistent proportions, high detail without photorealism, gentle storybook-lolita mood, refined textile and metal details, no 3D render, no toy-catalog plastic, no heavy oil-paint texture, no thick western cartoon outline, no chibi deformation unless requested.
```

## Qingyou Character Style Anchor

Use this block in every Qingyou generation prompt after the shared style anchor:

```text
Luo Qingyou style anchor: elegant Chinese-inspired classic Lolita with sage green, celadon, ivory, warm paper, antique gold, and soft umber palette; calm older-sister presence; graceful long dark hair; restrained facial features; plum or gold-green hair ornament; cloud collar, frog buttons, lace cuffs, layered skirt, fine embroidery, planner-and-tea atmosphere. Keep her line weight, face language, fabric rendering, and ornament density consistent with the source sheet.
```

## standard-full

Use case: stylized-concept  
Asset type: transparent character standing asset  
Primary request: Luo Qingyou full-body standard standing pose, regenerated from the reference crop.  
Subject: gentle older sister in sage green Chinese-inspired classic Lolita, ivory blouse, cloud collar, frog buttons, lace cuffs, embroidered skirt, long dark hair, small plum hairpin, project journal and vintage camera details.  
Style/medium: Japanese anime character design, clean lineart, soft cel shading, readable outfit construction.  
Composition/framing: full body centered, feet visible, neutral standing pose, generous padding.  
Constraints: no text, no labels, no sheet layout, no frame, no cast shadow, flat `#ff00ff` background.

## expressions

Use case: stylized-concept  
Asset type: transparent expression bust assets  
Primary request: regenerate one Luo Qingyou bust expression from the selected reference crop.  
Subject: same face, long dark hair, sage hair ornament, ivory blouse and green ribbon visible.  
Expression requirements: every expression must visibly differ through eyes, brows, mouth, head angle, hand gesture, or shoulder posture.  
Style/medium: Japanese anime expression reference, clean lineart, soft cel shading.  
Composition/framing: bust or half-body, centered, enough hair padding for cutout.  
Constraints: no text, no label, no frame, no shadow, flat `#ff00ff` background.

## poses

Use case: stylized-concept  
Asset type: transparent full-body pose asset  
Primary request: regenerate one Luo Qingyou action pose that preserves her sage classic Lolita silhouette and gentle planner identity.  
Pose options: photo taking, flipping journal, offering tea, preparing umbrella, adjusting Arisu's bow tie.  
Composition/framing: full body, centered, enough skirt and hair padding for cutout.  
Constraints: no text, no frame, no extra props beyond the chosen action, flat `#ff00ff` background.

## turnaround

Use case: stylized-concept  
Asset type: transparent turnaround view  
Primary request: regenerate the selected Luo Qingyou front, side, or back view as a single transparent asset.  
Subject: sage green Chinese classic Lolita outfit, cloud collar, frog buttons, lace sleeves, layered embroidered skirt, consistent long dark hair and accessory placement.  
Style/medium: production-ready anime character reference, clean lineart and flat-soft color.  
Composition/framing: one view only, full body, centered, feet visible.  
Constraints: no labels, no guide boxes, no text, no frame, flat `#ff00ff` background.

## clothing

Use case: stylized-concept  
Asset type: transparent clothing component  
Primary request: isolate and regenerate the selected Qingyou clothing component from the crop.  
Subject: sage green and ivory classic Lolita clothing, cloud collar, frog buttons, lace, embroidered skirt, gold details.  
Composition/framing: single clothing component or clean outfit fragment, centered with padding.  
Constraints: no mannequin unless necessary for readability, no text, no label, no frame, flat `#ff00ff` background.

## accessories

Use case: stylized-concept  
Asset type: transparent wearable accessory  
Primary request: regenerate the selected Qingyou accessory from the crop as an individual reusable asset.  
Subject: plum hairpin, frog buttons, lace cuffs, ribbons, gold-green ornamental details.  
Composition/framing: single accessory centered, readable silhouette, enough padding.  
Constraints: no text, no labels, no frame, no shadow, flat `#ff00ff` background.

## props

Use case: stylized-concept  
Asset type: transparent prop asset  
Primary request: regenerate the selected Qingyou prop from the crop as a clean item asset.  
Subject options: sage project journal, vintage camera, tea cup, portable bag, pen, bookmark.  
Style/medium: anime prop design, clean lineart, soft color, readable material details.  
Composition/framing: one object only, centered, generous padding.  
Constraints: no text, no label, no frame, no shadow, flat `#ff00ff` background.

## details

Use case: stylized-concept  
Asset type: transparent detail asset  
Primary request: regenerate the selected Qingyou design detail from the crop.  
Subject: hair ornament, fabric embroidery, waist ornament, lace sleeve details.  
Composition/framing: close-up component, centered, readable edges for cutout.  
Constraints: no text, no label, no frame, flat `#ff00ff` background.

## cg

Use case: illustration-story  
Asset type: future key visual reference  
Primary request: Luo Qingyou in an old street tea shop or rainy tea party day, keeping the same sage classic Lolita identity.  
Constraints: CG assets are not first-stage blockers; keep prompt drafts here until the sheet slots are stable.
