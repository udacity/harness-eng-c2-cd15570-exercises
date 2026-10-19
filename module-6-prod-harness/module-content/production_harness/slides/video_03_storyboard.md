# Storyboard — Video 3: Wire Controls to Lifecycle Boundaries

**Target runtime:** 7 minutes  
**Visual motif:** A vertical lifecycle with visible short circuits.

## Slide 1 — Placement is policy

**Time:** 0:00–0:35  
**On-screen text:** A correct control at the wrong boundary is not prevention.  
**Visual:** Permission shown first after execution with a red strike-through,
then before execution with a green check.

## Slide 2 — Skill availability versus delivery

**Time:** 0:35–1:20  
**Visual:** File exists → registered → session selected → pre-model evidence.  
**Callout:** Only selected context can influence this run.

## Slide 3 — Pre-tool order

**Time:** 1:20–2:30  
**Visual:** Permission → repeat → mutation safety → handler.  
**Required styling:** Permission denial exits before every downstream box.

## Slide 4 — Two prevention branches

**Time:** 2:30–3:25  
**Visual:** Side-by-side:

```text
deny:  no authority -> executed false
block: authority yes, invariant no -> executed false
```

## Slide 5 — Fresh evidence is state

**Time:** 3:25–4:10  
**Visual:** Health read sets a freshness badge; mutation consumes/invalidates
the badge.  
**Callout:** One read is not permanent authorization to mutate.

## Slide 6 — Handler and post-tool truth

**Time:** 4:10–4:55  
**Visual:** Only the handler can produce `executed: true`; post-tool records its
result and updates evidence.

## Slide 7 — Completion oracle

**Time:** 4:55–6:05  
**Visual:** Three mini-oracles combining final state with execute, deny, or
block evidence. A prose bubble is outside the oracle.

## Slide 8 — Exact vocabulary

**Time:** 6:05–7:00  
**Visual:** Proposed → denied/blocked/executed → completed, with “failed” on a
handler-error branch.  
**Transition:** Next: prove all three outcomes in real sessions.

## Production notes

- Use solid arrows for executed paths and stopped arrows for non-execution.
- Do not send denied calls through safety in the animation.
- Show completion nudge looping to the model with a bounded-counter badge.
- Repository captures: `before_tool`, `after_tool`, `before_completion`.
