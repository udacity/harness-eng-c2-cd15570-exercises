# Storyboard — Video 1: Evaluate the Harness, Not Only the Model

**Target runtime:** 6 minutes  
**Visual motif:** A layered system trace, with each layer producing a different
kind of evidence.

## Slide 1 — The engineering question

**Time:** 0:00–0:35  
**On-screen text:** Which components earn their production cost?  
**Visual:** Skills, evaluator, hooks, and permissions appear around the model;
question marks connect each to an evidence card.

## Slide 2 — Model versus harness evaluation

**Time:** 0:35–1:20  
**Visual:** Two columns.

| Model evaluation | Harness evaluation |
| --- | --- |
| Understand request | Supply missing knowledge |
| Choose action | Enforce authority and safety |
| Write response | Improve release quality |

**Callout:** Unit of analysis: the system.

## Slide 3 — Five separate facts

**Time:** 1:20–2:10  
**Visual:** Timeline with distinct rows for proposal, permission, hook,
execution/state, and evaluator.  
**On-screen text:** A response claim is not execution evidence.

## Slide 4 — Four component responsibilities

**Time:** 2:10–3:00  
**Visual:** Four cards:

- skills → private knowledge;
- permissions → authority;
- hooks → state validity;
- evaluator → response quality.

Do not draw overlapping arrows that imply interchangeability.

## Slide 5 — Hard gates, not one average

**Time:** 3:00–3:50  
**Visual:** Turnstile gates labeled task, safety, authorization, quality, and
coverage. Cost appears only after all gates.  
**Example:** High quality plus unauthorized execution remains disqualified.

## Slide 6 — Two cost boundaries

**Time:** 3:50–4:40  
**Visual:**

```text
serving: generator + online critic + revision
experiment: blind offline judge
```

**Callout:** Judge cost does not rank deployed configurations.

## Slide 7 — Minimum qualifying harness

**Time:** 4:40–5:30  
**Visual:** First filter configurations through qualification; then sort the
remaining cards by components, tokens, and time.  
**On-screen text:** Qualify first. Optimize second.

## Slide 8 — Takeaway

**Time:** 5:30–6:00  
**Full-screen statement:** “No component without an eval.”  
**Transition:** Next: comparisons that isolate one component.

## Production notes

- Never color a proposal as executed.
- Use separate icons for online critic and blind judge.
- Repository capture: `demo/agent.py`, then `demo/experiment.py`.
