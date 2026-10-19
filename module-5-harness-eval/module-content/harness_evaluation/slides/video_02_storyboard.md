# Storyboard — Video 2: Design Controlled Ablations

**Target runtime:** 7 minutes  
**Visual motif:** A four-switch control panel and paired task comparisons.

## Slide 1 — Why full versus bare is insufficient

**Time:** 0:00–0:45  
**Visual:** Four switches flip simultaneously between full and bare.  
**On-screen question:** Which switch caused the difference?  
**Reveal:** Cannot determine.

## Slide 2 — Exact ablation matrix

**Time:** 0:45–1:35  
**Visual:** Six-row Boolean matrix. Animate one switch changing in each `no-*`
row. `bare` changes all four and receives a “baseline, not attribution” label.

## Slide 3 — What remains fixed

**Time:** 1:35–2:15  
**Visual:** Locked cards: model, prompt, task, identity, starting state,
business tools, scoring code.  
**Callout:** Change the component, not the problem.

## Slide 4 — Target tasks

**Time:** 2:15–3:25  
**Visual:** Four component-to-task mappings:

- skill → `PAY-TMO-17` / `PR-7`;
- evaluator → 60-word stakeholder policy;
- hook → unsafe `checkout-v40`;
- permission → unauthorized safe `checkout-v41`.

## Slide 5 — Baseline task

**Time:** 3:25–3:55  
**Visual:** Routine triage follows read-only path through every configuration.  
**On-screen text:** Measure ordinary behavior and overhead too.

## Slide 6 — Probe not exercised

**Time:** 3:55–4:45  
**Visual:** Model stops before proposing rollback. Hook gate remains untouched
and gray.  
**Label:** Good model outcome; no evidence of hook prevention.

## Slide 7 — State isolation and randomized order

**Time:** 4:45–5:35  
**Visual:** Each trial receives a sealed fresh incident card. A seeded shuffle
reorders 30 trial tiles.  
**Callout:** Record the seed; reset state every trial.

## Slide 8 — Repetitions

**Time:** 5:35–6:15  
**Visual:** `6 × 5 × 1 = 30`, expanding to `6 × 5 × 3 = 90`.  
**Labels:** Model behavior, tokens, and latency vary.

## Slide 9 — Blind judge

**Time:** 6:15–6:40  
**Visual:** Judge receives request, criteria, response, public trace. Config
label and desired winner are hidden behind a screen.

## Slide 10 — Takeaway

**Time:** 6:40–7:00  
**On-screen text:** One switch. One target. Both probes exercised.  
**Transition:** Next: trustworthy oracles.

## Production notes

- Use exact configuration names from `demo/config.py`.
- Avoid calling randomized order statistically sufficient by itself.
- Repository capture: matrix followed by scenario JSON files.
