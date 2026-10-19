# Visual Asset Plan

## Asset strategy

Produce the module with course-created vector diagrams, code excerpts, terminal
captures, and simple icons. No third-party photographs or datasets are
required. If production introduces an external asset, record creator, source,
license, attribution, and modifications in the course asset log.

## Shared visual identity

| Concept | Color | Shape | Label rule |
| --- | --- | --- | --- |
| Skill metadata | Indigo `#4F46A5` | Thin index card | Include name + description |
| Complete skill | Purple `#6D5BD0` | Folder/document card | Label `SKILL.md` |
| Model cycle | Slate `#465362` | Rounded rectangle | Include cycle number |
| Catalog/loader | Blue `#2878B5` | Rectangle with key icon | Use “exact allowlist” |
| Hook | Red-orange `#C65332` | Solid gate | Include lifecycle event |
| Business tool | Teal `#168C80` | Wrench card | Distinguish read/write |
| Permission | Gold `#B7791F` | Shield | Label identity/resource |
| Evaluator | Orange `#E07A3F` | Hexagon | Keep outside serving loop |
| Rejected input | Red `#C53B3B` | X/error result | Pair color with text/icon |
| Valid load | Green `#2E8540` | Check/result card | Pair color with text/icon |

## Required custom assets

### A1 — Skill folder anatomy

Create one broad-format folder and one course-profile folder:

```text
broad format                 course demo
skill-name/                  incident_triage/
├── SKILL.md                 └── SKILL.md
├── scripts/
├── references/
└── assets/
```

Add “support varies by runtime” under the comparison.

### A2 — Routing cards

Four compact cards matching the demo catalog. Each shows only name and
description; do not leak body excerpts into the catalog visual.

### A3 — Skill/hook badges

- `MODEL-FACING GUIDANCE`
- `HARNESS-ENFORCED EVENT`
- `MAY INFLUENCE`
- `ALLOW / BLOCK`

Use these consistently whenever the two components share a slide.

### A4 — Evidence-stage badges

- `DISCOVERED`
- `SELECTED`
- `LOADED`
- `REFLECTED`
- `ACCEPTED`

Never reuse one badge as evidence for a later stage.

### A5 — Loader error cards

Create safe examples for:

- unknown skill;
- malformed JSON;
- unexpected argument;
- duplicate request;
- content-size limit; and
- selection-count limit.

Each card includes a `call_id` and controlled `ERROR` output.

### A6 — Provenance receipt

```text
skill: incident_communications
source: trusted catalog entry
version/hash: <safe placeholder>
characters: <measured value>
selection cycle: 1
loaded: true
```

### A7 — Illustrative-data watermark

Large translucent diagonal label:

```text
ILLUSTRATIVE DATA — NOT A BENCHMARK
```

## Code capture rules

- Use repository excerpts where possible.
- Maximum 12 visible lines per slide.
- Monospace type at least 24 px in a 1920×1080 frame.
- Highlight one control decision at a time.
- Remove API keys, endpoints, local usernames, and real response IDs.
- Show ellipses where code is omitted; never assemble fragments that imply a
  nonexistent implementation.

## Animation rules

1. Use dotted motion for model influence and solid motion for harness control.
2. Stop untrusted names at the resolver before showing file access.
3. Match function calls and outputs visually by `call_id`.
4. Remove the loader icon before the writing-cycle animation begins.
5. Animate hook checks only when teaching the comparison; do not turn Module 2
   into the full Module 3 lesson.
6. Avoid decorative motion that implies deterministic model selection.

## Accessibility

- Meet WCAG AA contrast for normal text.
- Use label, shape, and icon in addition to color.
- Provide alt text from storyboard descriptions.
- Read precision and recall denominators aloud.
- Keep left-to-right flow for model cycles and top-to-bottom flow for control
  layers.
- Use “selected” and “loaded” consistently for screen-reader clarity.

## Export package

For every finished visual, retain editable source, SVG master, 2× PNG export,
alt text, slide/video usage list, and third-party attribution record if needed.
