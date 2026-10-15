# Visual Asset Plan

## Asset strategy

The module can be produced entirely with course-created vector diagrams,
typography, code captures, and simple icons. No third-party photographs,
screenshots, or datasets are required.

This avoids unnecessary licensing risk and keeps the visual language consistent
with later harness modules. If a third-party asset is introduced during slide
production, record its creator, source URL, license, required attribution, and
modifications in the course's third-party asset log before use.

## Shared visual identity

| Concept | Color | Shape | Label rule |
| --- | --- | --- | --- |
| Generator | Purple `#6D5BD0` | Rounded rectangle | Always include “Generator” |
| Evaluator | Orange `#E07A3F` | Hexagon or sharp card | Use “Evaluator,” not “Judge” alone |
| Controller | Blue `#2878B5` | Rectangle with header band | Include stop-decision icon |
| Deterministic check | Teal `#168C80` | Square function card | Show exact expression where possible |
| Authoritative evidence | Slate `#465362` | Document card | Add source badge |
| Pass | Green `#2E8540` | Check icon | Pair color with text/icon |
| Failure | Red `#C53B3B` | X icon | Pair color with text/icon |
| Uncertain/escalate | Amber `#C78A16` | Triangle icon | Never use color alone |

## Required custom assets

### A1 — `INC-2048` evidence card

Fields:

```text
INC-2048 • checkout-api • DEGRADED • 18%
deployment: checkout-v42
rollback: false
recovery: false
```

Use as the stable source-of-truth visual in Videos 1–4.

### A2 — Flawed candidate card

Use the short scripted candidate from Video 1. Red underline unsupported
phrases. Add a small “SCRIPTED ILLUSTRATION” ribbon.

### A3 — Conversation identity badges

- `GEN-A` for generator branch
- `SELF-A` for same-conversation review
- `EVAL-B` for fresh evaluator branch

These badges make response-ID and context separation understandable without
showing provider-specific UI.

### A4 — Evidence badges

Reusable compact badges:

- `COUNTED BY CODE`
- `MATCHED TO SOURCE`
- `MODEL JUDGMENT`
- `HUMAN REVIEWED`
- `MALFORMED / NO DECISION`

### A5 — Controller stop signs

Four terminal icons with text:

- ACCEPTED
- RETRY
- FAILED
- ESCALATED

Do not represent FAILED or ESCALATED as crashes; they are intentional harness
outcomes.

### A6 — Illustrative-data watermark

Large translucent diagonal label:

```text
ILLUSTRATIVE DATA — NOT A BENCHMARK
```

Use on every Video 5 metric visual.

## Code visuals

- Use a monospace font at least 24 px in a 1920×1080 frame.
- Show no more than 12 code lines on a slide.
- Highlight one expression at a time.
- Replace API keys, endpoints, and response IDs with safe placeholders.
- Prefer repository excerpts over simulated terminal chrome.

## Animation rules

1. Use progressive reveal to establish causal order.
2. Keep the controller visible whenever accept/retry/fail is discussed.
3. Animate error evidence before the verdict so the verdict does not appear
   magical.
4. Avoid decorative motion that implies model reasoning is deterministic.
5. Keep transitions under 400 ms unless the instructor is narrating a process.

## Accessibility

- Minimum text contrast: WCAG AA for normal text.
- Never encode pass/fail by red and green alone.
- Provide alt text from storyboard notes.
- Read equations and denominators aloud.
- Keep diagram arrow directions consistent: left-to-right for flow,
  top-to-bottom for evaluation layers.
- Avoid rapid flashing and dense moving backgrounds.

## Export package

For each final visual, retain:

- editable source;
- SVG master;
- PNG export at 2× slide resolution;
- alt text;
- slide/video usage list; and
- third-party attribution record, if applicable.
