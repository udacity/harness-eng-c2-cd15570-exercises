# Storyboard — Video 5: Interpret Results and Continue Evaluation

**Target runtime:** 7 minutes  
**Visual motif:** Four paired comparisons converge on a scoped recommendation,
then reopen into a continuous evaluation loop.

## Slide 1 — Captured result

**Time:** 0:00–0:50  
**Visual:** Six-row table with success, quality, invalid, unauthorized. Label:
“one repetition; captured model run.”  
**Highlight:** Only `full` passes all gates.

## Slide 2 — Skills pair

**Time:** 0:50–1:40  
**Visual:** Full contains Payments Runtime and `PR-7`; no-skills omits them.
Both show quality 5.00.  
**Takeaway label:** Exact domain oracle catches what prose score misses.

## Slide 3 — Evaluator pair

**Time:** 1:40–2:30  
**Visual:** Initial stakeholder response → critic findings → text-only revision
→ policy pass. No-evaluator path ends with omissions.  
**Takeaway:** Release quality, not side-effect safety.

## Slide 4 — Hook pair

**Time:** 2:30–3:20  
**Visual:** Both propose v40. Full stops at hook; no-hooks executes and changes
state.  
**Takeaway:** Prevention at the execution boundary.

## Slide 5 — Permission pair

**Time:** 3:20–4:10  
**Visual:** Both propose safe v41. Full denies Sam; no-permissions passes safety
and executes.  
**Takeaway:** Safe does not mean authorized.

## Slide 6 — Bare baseline

**Time:** 4:10–4:50  
**Visual:** Low-token badge beside 20% success, one invalid, one unauthorized,
and mean quality 4.12.  
**Callout:** Cheap failed requirements do not qualify.

## Slide 7 — Supported versus unsupported claim

**Time:** 4:50–5:35  
**Visual:** Green scoped statement references model, suite, policy, thresholds,
and run. Red crossed-out statement says every agent needs all four components.

## Slide 8 — Next experiment

**Time:** 5:35–6:20  
**Visual:** Expansion rings: repetitions, held-out tasks, paraphrases,
adversarial cases, separate judge, expert audit, production-derived cases.

## Slide 9 — Continuous evaluation loop

**Time:** 6:20–6:45  
**Visual:** Logs/failures → curated cases → eval suite → change gate → monitored
deployment → new logs.

## Slide 10 — Final takeaway

**Time:** 6:45–7:00  
**Full-screen statement:** Keep only what earns its place for the workload—but
require complete evidence before removing a boundary.

## Production notes

- Use the exact captured figures from the current report if re-recorded.
- Label all result slides with repetition count and model identity.
- End on the evaluation lifecycle, not on `full` as a permanent winner.
