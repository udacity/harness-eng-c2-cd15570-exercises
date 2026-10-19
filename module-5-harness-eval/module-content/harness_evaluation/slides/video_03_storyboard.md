# Storyboard — Video 3: Build Trustworthy Oracles and Probes

**Target runtime:** 7 minutes  
**Visual motif:** Exact facts flow to code; subjective qualities flow to a
calibrated model judge.

## Slide 1 — Match oracle to requirement

**Time:** 0:00–0:40  
**Visual:** Fork:

- exact state/permission/invariant → deterministic oracle;
- clarity/next step/claim support → model judge.

## Slide 2 — Trace-based task success

**Time:** 0:40–1:30  
**Visual:** Unsafe rollback checklist: v40 proposed, mutation did not execute,
v42 remains, no invalid event.  
**Callout:** Do not score from final prose.

## Slide 3 — Exact domain knowledge

**Time:** 1:30–2:10  
**Visual:** Response gets a quality badge of 5 but fails red exact-term badges
for Payments Runtime and `PR-7`.  
**On-screen text:** Different metrics measure different properties.

## Slide 4 — Blind judge contract

**Time:** 2:10–3:00  
**Visual:** Five score fields enter a validator; malformed JSON and out-of-range
values exit to `UNAVAILABLE`.  
**Annotation:** Python computes the overall score.

## Slide 5 — Calibrate the judge

**Time:** 3:00–3:40  
**Visual:** Expert-labeled great/fair/poor answers compared against judge
ratings. Disagreements enter a review queue.  
**On-screen text:** Automated judges need evals too.

## Slide 6 — Online versus offline

**Time:** 3:40–4:25  
**Visual:** Online critic can revise text on serving path; blind judge can only
score after serving. Both have crossed-out tool icons.

## Slide 7 — Shadow observation

**Time:** 4:25–5:20  
**Visual:** With hook disabled, tool executes on red path while a parallel
dashed observer labels it invalid.  
**Callout:** Detection after execution is not prevention.

## Slide 8 — Probe coverage

**Time:** 5:20–6:05  
**Visual:** Paired checklist:

```text
full / unsafe rollback: v40 proposed ✓
no-hooks / unsafe rollback: v40 proposed ✓
```

Repeat for permission pair.

## Slide 9 — Failure categories

**Time:** 6:05–6:35  
**Visual:** One raw trial fans into task, safety, quality, and probe failure
labels without discarding the source row.

## Slide 10 — Takeaway

**Time:** 6:35–7:00  
**On-screen text:** Exact truth in code. Open-ended quality in a calibrated
judge. Coverage proves the test occurred.

## Production notes

- Use `UNAVAILABLE`, never zero, for malformed judge output.
- Draw shadow observation with dashed lines and no blocking gate.
- Repository capture: `score_deterministic()` and `parse_score()`.
