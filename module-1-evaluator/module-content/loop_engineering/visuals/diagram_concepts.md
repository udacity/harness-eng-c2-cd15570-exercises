# Diagram Concepts

These concepts are production notes for slide designers. Use the shared visual
language in `visual_assets.md` and keep labels consistent with the narration.

## D1 — The self-validation loop

**Used in:** Video 1, Slides 1 and 6  
**Question answered:** Where is acceptance authority located?

```text
User request -> Generator -> Candidate
                    ^           |
                    |           v
                    +---- Same conversation reviews
                                      |
                               “Looks good” -> Stop
```

Design the generator and self-review as one purple boundary to make shared
context visible. Place a red unsupported-claim marker on the candidate and let
it pass through the review unchanged.

**Do not depict:** the model as intentionally deceptive. The risk is shared
context and weak evidence, not motive.

## D2 — Apparent versus verified success

**Used in:** Video 1, Slide 2

Two vertical lanes:

- Apparent: API returned, response exists, grammar is clean, self-review says
  pass.
- Verified: 60 words counted, incident ID found, claims mapped to evidence,
  next step judged useful.

Use gray checkmarks for observations and green evidence badges for verified
criteria. The visual must not imply apparent signals are useless; they are just
insufficient.

## D3 — Three responsibility cards

**Used in:** Video 2, Slides 1–4

Three cards arranged left to right:

1. **Generator** — “produce / revise candidates”
2. **Evaluator** — “apply rubric / return findings”
3. **Controller** — “combine evidence / own stop rule”

Give each exactly one primary verb line. Avoid a fourth “agent” box that makes
ownership ambiguous.

## D4 — Same model, separate context

**Used in:** Video 2, Slide 5

Show two API envelopes both labeled `model: gpt-x`:

- Envelope A: generator instructions + task context + conversation A
- Envelope B: evaluator instructions + evidence + candidate; no conversation A

Add a callout: “role/context separation; correlated model risk remains.” A
dotted optional path may replace Envelope B with a different model.

## D5 — Layered evaluation funnel

**Used in:** Video 3, Slide 5

Candidate enters a wide blue exact-check layer. Failures exit with direct
findings. Passing candidates enter a narrower orange inferential layer. The
controller sits below both and receives every result.

Include small cost markers:

```text
exact checks: low variable cost / reproducible
model review: token + latency cost / probabilistic
```

Avoid absolute “cheap” and “expensive” labels without context.

## D6 — Bounded evaluation loop

**Used in:** Video 4

Place the controller at the center rather than drawing a free-running cycle:

```text
controller -> generate -> evaluate -> controller
      |                         |
      +-> accept/fail/escalate  +-> findings
```

Place attempt, token, cost, and time gauges on the controller. This reinforces
that the models do not own budgets or stopping.

## D7 — Criterion history heatmap

**Used in:** Video 4, Slide 7

Rows are attempts; columns are criteria. Use icons in addition to color:

- green check: passed;
- red X: failed;
- amber triangle: evaluator error or unavailable;
- gray dash: not run.

Include an example regression where fixing word count introduces an unsupported
recovery claim.

## D8 — Measurement fork

**Used in:** Video 5, Slide 2

One held-out case set forks into self-review and independent-evaluation paths.
Both end at the same reference scorer. Lock icons label held-constant
generation settings. Repeated samples appear as stacked copies, not one line.

## D9 — Acceptance confusion matrix

**Used in:** Video 5, Slide 3

Use “reference acceptable/unacceptable” on the horizontal axis and “harness
accept/reject” on the vertical axis. Label cells with both names and counts:

- accepted + acceptable: accepted correctly;
- accepted + unacceptable: false acceptance;
- rejected + acceptable: false rejection;
- rejected + unacceptable: rejected correctly.

Do not abbreviate to TP/FP until after plain-language labels appear.

## D10 — Verification selection tree

**Used in:** Video 5, Slide 7

```text
Can the requirement be computed exactly?
  yes -> deterministic check
  no  -> Is semantic error consequential?
           yes -> calibrated evaluator, often with human escalation
           no  -> lightweight review or human-at-release workflow
```

Show that exact and inferential checks can coexist. This is a routing aid, not
a universal risk policy.
