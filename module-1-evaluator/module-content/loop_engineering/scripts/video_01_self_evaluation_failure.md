# Video 1 — When Agents Judge Their Own Work

**Target duration:** 6 minutes  
**Learning objective:** Explain why same-conversation self-review is useful
feedback but weak acceptance evidence.

## Instructor narration

### [Slide 1] A polished failure — 0:00–0:55

Let’s begin with an incident update that looks finished:

> INC-2048 is resolved after the team rolled checkout-api back to
> checkout-v41. Error rates are normal, customers can check out successfully,
> and the team will continue monitoring.

It is concise. It is confident. It sounds like something we could paste into a
status channel. It is also wrong.

The authoritative ticket says the service is still degraded at an 18 percent
error rate. No rollback has occurred. Recovery is not confirmed. The request
also requires exactly 60 words, and this update is much shorter.

Now imagine we continue the same model conversation and ask, “Did you satisfy
all the requirements?” In this scripted illustration, the model responds:

```text
WORD_COUNT: PASS
INCIDENT_ID: PASS
FACTUAL_GROUNDING: PASS
USEFUL_NEXT_STEP: PASS
VERDICT: PASS
```

The review sounds structured, but structure is not evidence. We can count the
words ourselves and read the contradictory incident state. The model's
confidence does not repair the candidate.

### [Slide 2] Apparent success versus actual success — 0:55–1:45

This is the distinction we will use throughout the course.

Apparent success means the response exists, reads well, and the model says it
is done. Actual requirement satisfaction means we have evidence for each
acceptance criterion.

For this task, two criteria are exact. Does the candidate contain `INC-2048`?
Does `candidate.split()` produce exactly 60 words? We do not need another
language-model opinion for either question.

Other criteria require judgment. Are the claims grounded in the incident
snapshot? Is the next diagnostic step useful and safe? Those checks need
evidence-aware review, but they still need explicit decisions and reasons.

The first engineering lesson is simple: successful generation is not the same
event as successful verification.

### [Slide 3] Failure pattern one: the yes-agent trap — 1:45–2:45

The first failure pattern is the sycophantic yes-agent trap. The model has just
created an answer. We ask a broad question such as, “Did you do a good job?”
That question supplies no rubric and invites agreement.

The same conversation also contains the path that produced the answer. Its
review can reuse the same assumptions, attend to the same details, and overlook
the same omission. Familiarity with an answer is not independent support for
it.

We should be careful with the claim. Self-review does not always fail. There is
research and practical experience showing that feedback and revision can
improve model output. The problem is narrower: the author should not be the
sole acceptance authority, especially when an exact or external check is
available.

Ask for criteria, findings, and evidence—not a general expression of
confidence.

### [Slide 4] Failure pattern two: premature exit — 2:45–3:45

The second pattern is premature exit. One observable signal passes, and the
system treats that as completion.

A Python file can execute without a syntax error and still calculate the wrong
result. Every requested file can exist while a feature is missing. A report can
be grammatical while citing facts that the source never established. A status
update can contain the incident ID while inventing a rollback.

These examples separate execution checks from task checks. “The call returned”
is an execution fact. “The requested result is correct” is a task claim. The
harness needs a stopping condition tied to task evidence.

In the Module 1 basic loop, the generator writes a draft and then rewrites it
for clarity. Two cycles occur, but neither candidate is evaluated. The loop
stops because its cycle count is exhausted, not because quality was proven.

### [Slide 5] Failure pattern three: vibe acceptance — 3:45–4:45

The third pattern is normalization of deviance, or what we might call “vibe
accept.” A response looks approximately right, so we accept it. Later, that
response becomes an example, a cached answer, or context for another agent.
Weak acceptance criteria can amplify the original error.

If this happens repeatedly, the practical standard shifts from “satisfies the
requirements” to “nothing looked obviously wrong.” The system may report high
completion even as unsupported claims accumulate.

The IKEA effect is a useful human analogy: people can value work more after
helping create it. But it is only an analogy here. It does not prove that every
model has a human sense of ownership. Our engineering argument does not depend
on model psychology. It depends on observable correlated errors and weak
verification boundaries.

### [Slide 6] Change the stop rule — 4:45–5:40

Here is the weak loop:

```text
request -> generator -> candidate -> same conversation says “looks good” -> stop
```

The generator both writes the candidate and supplies the only reason to accept
it. Even if the prompt says “be critical,” acceptance still depends on one
context and one authority.

The improvement is not “ask the model to think harder.” The improvement is to
move the acceptance decision into the harness. Give exact requirements to
code. Give judgment-based requirements to a separately instructed evaluator.
Require named findings. Let a controller—not either model—decide whether the
candidate passes, should be revised, or must fail.

### [Slide 7] Transition — 5:40–6:00

In the next lesson, we will separate three responsibilities: a generator that
produces candidates, an evaluator that tests them against explicit criteria,
and a controller that owns retries and stopping.

The goal is not to distrust every model answer. The goal is to stop treating
confidence as the acceptance test.

## Demonstration note

The deliberately positive self-review on Slide 1 is a scripted teaching
illustration, not a promised live-model result. In a live demonstration, show
the actual candidate and verdict. If self-review catches every problem, say so;
then emphasize that the acceptance path still lacks evidence independent of
the generator conversation.

## Transition line

> We have seen why author and acceptance authority should not be identical.
> Now let’s design the three-part architecture that separates them.
