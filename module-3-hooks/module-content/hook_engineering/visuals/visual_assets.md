# Visual Asset Plan

## Asset strategy

Use course-created vector diagrams, code excerpts, state cards, truth tables,
and terminal captures. No third-party photographs or datasets are required. If
an external asset is introduced, record its creator, source, license,
attribution, and modifications in the course asset log.

## Shared visual identity

| Concept | Color | Shape | Label rule |
| --- | --- | --- | --- |
| Model proposal | Purple `#6D5BD0` | Dotted-edge card | Always say “proposed” |
| Hook lifecycle event | Blue `#2878B5` | Socket/gate | Include event name |
| Antidote/check | Teal `#168C80` | Square function card | Include invariant name |
| Trusted state | Slate `#465362` | Versioned document | Show source/version badge |
| Permission | Gold `#B7791F` | Shield | Use “authorized/denied” |
| Tool execution | Dark green `#236B42` | Wrench/solid arrow | Include executed evidence |
| Block/failure | Red `#C53B3B` | Stop octagon | Pair color with text/icon |
| Hook error | Amber `#C78A16` | Warning diamond | Fail-closed label |
| Evaluator | Orange `#E07A3F` | Hexagon | Place after candidate/output |

## Required custom assets

### A1 — Incident state card

```text
INC-2048 • production • checkout-api
health: DEGRADED • recovery: false
current: checkout-v42
last-known-good: checkout-v41
```

### A2 — Mutation proposal cards

- `rollback_deployment(INC-2048, checkout-v40)`
- `rollback_deployment(INC-2048, checkout-v41)`
- `update_incident_status(INC-2048, RESOLVED)`

Every card has a `PROPOSED — NOT EXECUTED` ribbon until dispatch evidence.

### A3 — Antidote cards

Create ten reusable cards matching the incident and expense antidote catalog.
Each includes failure, predicate, and one boundary test.

### A4 — Decision badges

- `PASS`
- `FAIL`
- `ERROR — FAIL CLOSED`
- `NOT APPLICABLE`
- `ALLOW`
- `BLOCK`
- `NOT RUN`
- `NOT CHECKED`

Never use `PASS` for a hook that was not invoked.

### A5 — Execution receipt

```text
requested: true
hook_executed: true
decision: BLOCK
tool_executed: false
state_changed: false
policy_version: <safe placeholder>
```

### A6 — Exact-money number line

Use cent increments only around the thresholds. Avoid a continuous graphic that
suggests values between cents are valid inputs.

### A7 — State-version tokens

Reusable badges: `v17 CHECKED`, `v18 CURRENT`, `EXPECTED VERSION CONFLICT`.

### A8 — Illustrative-data watermark

Large translucent diagonal text:

```text
ILLUSTRATIVE DATA — NOT A BENCHMARK
```

## Code capture rules

- Use repository excerpts where possible.
- Show no more than 12 lines at once.
- Use monospace type at least 24 px at 1920×1080.
- Highlight the early return before dispatch.
- Show exact comparison operators at thresholds.
- Remove API keys, private endpoints, usernames, and real response IDs.
- Mark pseudocode clearly when code is not copied from the repository.

## Animation rules

1. A proposal never crosses the gate before checks appear.
2. Animate violation evidence before the block decision.
3. On block, stop and fade the tool arrow; do not animate a mutation.
4. On allow, show tool execution as a separate event.
5. Invalidate old evidence immediately after the state-change animation.
6. Keep state versions visible during TOCTOU sequences.
7. Avoid motion suggesting hooks make model choices deterministic.

## Accessibility

- Meet WCAG AA contrast for normal text.
- Use icon, label, and shape in addition to color.
- Read exact threshold operators aloud.
- Provide alt text from storyboard visual descriptions.
- Keep causal order left to right and control layers top to bottom.
- Do not use rapid flashing for block events.

## Export package

For every final visual, retain editable source, SVG master, 2× PNG export, alt
text, slide/video usage list, and third-party attribution record if needed.
