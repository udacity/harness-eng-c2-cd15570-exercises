# Storyboard — Video 4: Prove Useful and Safe Operation

**Target runtime:** 8 minutes  
**Visual motif:** Three controlled runs feeding a four-artifact evidence panel.

## Slide 1 — Runtime proof

**Time:** 0:00–0:40  
**On-screen text:** Fresh state. Exact boundary. Authoritative evidence.  
**Visual:** Reset icon before three scenario lanes.

## Slide 2 — Safe rollback

**Time:** 0:40–2:00  
**Visual:** Morgan → permission allow → safety allow → rollback executes → v41.  
**Callout:** Positive control proves usefulness.

## Slide 3 — Unauthorized rollback

**Time:** 2:00–3:05  
**Visual:** Sam → permission deny → stop → v42. Safety and handler boxes are
dimmed and labeled “not reached.”

## Slide 4 — Unsafe rollback

**Time:** 3:05–4:10  
**Visual:** Morgan → permission allow → safety block v40 → stop → v42.  
**Callout:** Authorized does not mean valid.

## Slide 5 — Four artifacts

**Time:** 4:10–5:15  
**Visual:** Four cards:

- state: what is true;
- trace: why;
- usage: inference work;
- summary: derived scenario status.

## Slide 6 — Exit versus completion

**Time:** 5:15–6:00  
**Visual:** `returncode: 0` and fluent prose fail to open a completion gate;
state plus trace opens it.

## Slide 7 — Stable invariants, variable path

**Time:** 6:00–7:10  
**Visual:** Several model-path squiggles converge on the same required boundary
and final state.  
**Callout:** Extra calls vary; the oracle does not.

## Slide 8 — Combined proof

**Time:** 7:10–8:00  
**Visual:** Execute, deny, and block form a three-part shield around “useful
production operation.”  
**Transition:** Next: tests, diagnosis, and maintenance.

## Production notes

- Capture the current artifacts immediately after each run.
- Never reuse safe-run state while narrating a prevented case.
- Label trace excerpts “illustrative” if model-dependent extra events are
  omitted.
- Narrate an incomplete live run honestly if `completed` is false.
