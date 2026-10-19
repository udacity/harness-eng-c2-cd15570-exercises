# Diagram Concepts

## Visual language

Use one consistent visual grammar across all five videos:

| Concept | Shape | Suggested color | Meaning |
| --- | --- | --- | --- |
| Runtime mechanism | Rounded rectangle | Slate | Framework-owned lifecycle |
| Domain component | Rectangle | Blue | Plugin-owned implementation |
| Trusted state/evidence | Document or database | Teal | Authoritative fact |
| Permission decision | Diamond | Amber | Authority gate |
| Hook decision | Hexagon | Purple | Deterministic lifecycle rule |
| Execution | Solid gear | Green | Handler ran |
| Denial | Stop bar | Orange | Insufficient authority |
| Safety block | Shield/stop | Red-purple | Invalid state transition |
| Model prose | Speech bubble | Gray | Non-authoritative narrative |

Never use the same symbol for permission denial and safety block. Both prevent
execution, but they answer different questions.

## Concept 1 — The ownership seam

Place Hermes on the left and the incident plugin on the right. Connect them
only through named registration and callback ports. Put model lifecycle,
continuation, session bounds, and usage inside Hermes. Put tools, skills,
permissions, hooks, oracle, and domain trace inside the plugin.

The launcher appears above both as a thin “prepare and invoke” strip. It must
not contain an internal model/tool cycle.

## Concept 2 — Proof ladder

Build a vertical ladder:

1. files parse;
2. package validates;
3. deterministic components pass;
4. local integration short-circuits correctly;
5. live scenarios reach boundaries;
6. artifacts reconcile.

Each rung supports a different claim. Avoid a single “passed” badge spanning
the entire ladder.

## Concept 3 — Selective gate

Show three operators approaching the same mutation endpoint:

- Morgan with v41 passes both permission and safety;
- Sam with v41 stops at permission;
- Morgan with v40 passes permission and stops at safety.

This image should communicate that usefulness and prevention are simultaneous,
not opposing, goals.

## Concept 4 — Evidence freshness

Represent fresh health as a per-session token created by a successful health
tool result. A mutation consumes or invalidates the token. A later mutation
without another health read encounters a missing-token block.

Do not portray skill context or model recollection as fresh operational
evidence.

## Concept 5 — Completion balance

Use a two-pan scale. One pan holds final state. The other holds the relevant
trace event. Both must balance before the completion gate opens.

Examples:

- v41 plus executed rollback;
- unchanged v42 plus permission deny; and
- unchanged v42 plus safety block.

A speech bubble reading “done” floats outside the scale.

## Concept 6 — Two harnesses, one behavioral bar

The exercise comparison should not look like a race. Use parallel lanes with
the same finish criterion: the fixed client behavioral test. After both pass,
the lanes feed a responsibility table.

Avoid winner podiums based on elapsed time, source style, or line count.

## Accessibility

- Pair every color with a shape and text label.
- Maintain high contrast for trace excerpts and code captures.
- Use solid versus dashed lines in addition to color.
- Keep decision labels on arrows, not only in legends.
- Announce initial and final deployments aloud.
- Avoid rapid scrolling through JSONL; isolate the relevant fields.
- Provide text alternatives for every architecture and scenario visual.
