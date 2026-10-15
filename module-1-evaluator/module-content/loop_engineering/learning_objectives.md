# Learning Objectives

## Module-level objectives

By the end of this module, learners will be able to:

1. **Distinguish generation from acceptance.** Explain why a generated answer,
   successful API call, clean syntax, or confident self-review does not by
   itself establish task completion.
2. **Identify correlated evaluation risk.** Describe how a generator and a
   same-conversation reviewer can share assumptions, omissions, and framing
   without claiming that self-review always fails.
3. **Design separated responsibilities.** Assign candidate production to a
   generator, criterion assessment to an evaluator, and retries and stopping to
   a harness controller.
4. **Write measurable criteria.** Convert vague requirements such as “make it
   good” into observable pass/fail conditions with evidence.
5. **Choose the right verification mechanism.** Prefer deterministic code for
   exact properties and use inferential evaluation only for criteria requiring
   semantic judgment.
6. **Build a bounded evaluation loop.** Feed specific findings into revision,
   re-evaluate the new candidate, enforce attempt and budget limits, and report
   unresolved failure honestly.
7. **Interpret evaluator error.** Define false acceptance and false rejection,
   and explain why an independent LLM evaluator still requires calibration.
8. **Measure engineering value.** Compare output quality, error rates,
   iterations, tokens, cost, and latency against an external reference set.
9. **Choose an appropriate evaluator design.** Decide when deterministic checks
   are sufficient, when an independent model is justified, and when a separate
   model or human escalation adds value.

## Lesson-level objectives

### Video 1 — Self-evaluation failure

Learners can:

- locate explicit requirement violations in a fluent candidate;
- explain the yes-agent trap, premature exit, and vibe acceptance;
- separate apparent success from verified requirement satisfaction; and
- use the IKEA effect only as an analogy for overvaluing one's work, not as a
  claim about universal model psychology.

### Video 2 — Independent evaluator

Learners can:

- diagram generator, evaluator, and controller responsibilities;
- explain why independent context matters;
- distinguish role separation from cross-model evaluation; and
- explain the limited structural analogy to adversarial systems without
  describing the harness as GAN training.

### Video 3 — Evaluation criteria

Learners can:

- classify requirements as deterministic or inferential;
- construct a five-criterion rubric containing both types;
- order inexpensive exact checks before model-based checks; and
- require evidence and actionable feedback for every failure.

### Video 4 — Evaluation loop

Learners can:

- implement generate–evaluate–revise–re-evaluate orchestration;
- preserve separate conversation branches;
- parse structured findings and fail closed;
- enforce maximum attempts, token budgets, and quality thresholds; and
- record and escalate a terminal failure rather than relabeling it as success.

### Video 5 — Measuring improvement

Learners can:

- compute acceptance rate, false acceptance rate, and false rejection rate;
- compare initial and final quality using the same reference standard;
- separate serving cost from evaluation overhead;
- interpret quality improvement per unit of cost; and
- decide whether the evaluator should remain, be narrowed, or be replaced by
  deterministic verification.

## Suggested knowledge checks

1. A model produces valid JSON containing a factually unsupported claim. Which
   part should code check, and which part requires evidence-based judgment?
2. An evaluator returns “mostly good” without named criteria. Should the
   controller accept? Why?
3. The third revision still fails one required criterion. The retry limit is
   three. What terminal state should the harness record?
4. The same model is used in two fresh calls with different instructions. Is
   the evaluator independent? What risks remain?
5. An external evaluator reduces false acceptance but doubles latency. What
   additional evidence is needed before deciding whether to keep it?

## Performance assessment

A learner demonstrates mastery by producing a small harness that:

- creates generator and evaluator calls with separate contexts;
- evaluates at least five named criteria;
- includes at least two deterministic and two inferential checks;
- returns machine-readable findings with cited evidence;
- retries only from explicit feedback;
- stops at a fixed maximum without false success;
- logs candidate, checks, verdict, tokens, and latency for each attempt; and
- compares its decisions with a verified reference set.
