# Storyboard — Video 4: Qualify and Rank the Minimum Harness

**Target runtime:** 7 minutes  
**Visual motif:** Evidence passes through readiness, coverage, and qualification
gates before a small cost-ranking podium.

## Slide 1 — Two questions before ranking

**Time:** 0:00–0:35  
**On-screen text:** Is the study complete? Which configurations qualify?  
**Visual:** Cost podium remains covered until both questions pass.

## Slide 2 — Exact planned keys

**Time:** 0:35–1:25  
**Visual:** Grid of configuration × task × repetition. One missing tile and one
duplicate tile both turn readiness red.  
**Callout:** Set equality plus row-count equality.

## Slide 3 — Global versus filtered scope

**Time:** 1:25–2:05  
**Visual:** Complete 6×5 grid beside a one-cell debug run.  
**Labels:** Global recommendation versus local diagnosis.

## Slide 4 — Value plus coverage

**Time:** 2:05–2:50  
**Visual:** Metric card has two mandatory fields: `unauthorized=0` and
`coverage=100%`. Remove one observation; the card becomes unknown.  
**On-screen text:** Missing is not zero.

## Slide 5 — Mean can hide a failure

**Time:** 2:50–3:35  
**Visual:** Four high quality bars and one low stakeholder bar. Mean reads 4.76;
minimum exposes 3.80.  
**Callout:** Inspect task-level and worst observed outcomes.

## Slide 6 — Qualification gates

**Time:** 3:35–4:30  
**Visual:** Gates for success, quality, invalid=0, unauthorized=0, coverage, and
probes. Every configuration card must pass all gates.

## Slide 7 — Cost only after qualification

**Time:** 4:30–5:15  
**Visual:** Qualifiers sort by components, serving tokens, model seconds, name.
Nonqualifiers are not placed on the podium regardless of cost.

## Slide 8 — Cost boundary

**Time:** 5:15–5:50  
**Visual:** Online critic/revision tokens enter serving column. Blind judge
tokens enter benchmark-overhead column and stop before ranking.

## Slide 9 — Evidence artifacts

**Time:** 5:50–6:25  
**Visual:** Raw CSV → failures JSON → generated Markdown report. Checkpoint icon
appears after every trial.  
**Callout:** Read raw rows before conclusions.

## Slide 10 — Takeaway

**Time:** 6:25–7:00  
**On-screen pipeline:** Validate plan → verify coverage → aggregate → qualify →
rank.  
**Transition:** Next: interpret the captured result.

## Production notes

- Label the mean/minimum example as captured, not universal.
- Do not show a weighted composite score.
- Repository capture: `_study_readiness()`, `qualifying_configs()`, report.
