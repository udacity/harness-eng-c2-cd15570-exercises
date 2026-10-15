# Video 3 — Build Evaluators from Measurable Criteria

**Target duration:** 6 minutes 30 seconds  
**Learning objective:** Divide a rubric into deterministic and inferential
checks, and order those checks by cost and evidentiary strength.

## Instructor narration

### [Slide 1] “Make it good” is not a test — 0:00–0:50

An evaluator cannot assess success reliably until we define success.

“Write a good incident update” sounds reasonable to a person, but it does not
tell a harness what must be present, what must be absent, what evidence to use,
or how to stop.

Compare that with: “Write exactly 60 words, include `INC-2048`, use only facts
in the incident snapshot, do not claim an unobserved action or recovery, and
give one safe next diagnostic step.”

Now we have observable criteria. The next question is how each one should be
checked.

### [Slide 2] Deterministic checks — 0:50–1:45

Deterministic checks compute an answer from an explicit rule. For the incident
update, Python can count whitespace-delimited words and test for the exact
incident identifier.

```python
word_count_ok = len(candidate.split()) == 60
incident_id_ok = "INC-2048" in candidate
```

Other examples include JSON schema validation, unit tests, type checking,
required file names, prohibited terms, YAML parsing, secret scanning, and
character limits.

These checks are usually faster, cheaper, and more reproducible than asking a
model. More importantly, they produce direct evidence. If the requirement is
“exactly 60 words,” a model's estimate should not override the count.

### [Slide 3] Inferential checks — 1:45–2:40

Inferential checks handle requirements that need semantic judgment. Is the
candidate grounded in the incident facts? Does the next step help diagnose the
problem without implying an unsafe production change? Is the explanation
technically coherent?

An evaluator model can assess those questions, but the result is probabilistic.
We should provide the original requirement, the relevant evidence, and a
criterion-specific output format. We should also validate the evaluator against
representative examples rather than assuming its labels are correct.

Inferential does not mean vague. “Factual grounding: pass only if every factual
claim is supported by the supplied snapshot” is far more testable than “Does
this look accurate?”

### [Slide 4] A five-criterion rubric — 2:40–3:40

Here is a practical rubric for `INC-2048`:

| Criterion | Type | Pass condition |
| --- | --- | --- |
| Word count | Deterministic | `split()` returns exactly 60 words |
| Incident ID | Deterministic | Exact token `INC-2048` appears |
| Required format | Deterministic | One paragraph; no heading or bullet prefix |
| Factual grounding | Inferential | Every claim is supported by the snapshot |
| Useful next step | Inferential | Names a safe diagnostic action before mutation |

We could add a sixth inferential criterion for action-state consistency: the
response must not describe a rollback, restart, recovery, or resolution unless
the authoritative evidence says it occurred.

Notice that each criterion says how to pass. The evaluator should return a
decision, evidence, and actionable feedback for every failure.

### [Slide 5] Layer checks by cost — 3:40–4:35

Run inexpensive exact checks first.

```text
candidate
   |
   v
schema, required fields, counts, tests
   | fail ----------------------> return exact findings
   v pass
semantic evaluator
   | fail ----------------------> return grounded findings
   v pass
controller may accept
```

If the candidate is invalid JSON, there may be no reason to pay for a model to
review its prose. If the word count is wrong and the controller permits a cheap
revision, fix that before deeper review.

This ordering is a default, not a law. Sometimes one evaluator call can assess
several expensive criteria more efficiently than repeated calls. The harness
should make that tradeoff explicit and measure it.

### [Slide 6] The pattern transfers across domains — 4:35–5:35

The same split applies beyond incident response.

For coding, tests, linting, and types are deterministic; design correctness and
requirement satisfaction may need review.

For SEO, tag lengths and heading structure are exact; relevance and content
quality require judgment.

For marketing, prohibited words and layout rules are exact; brand voice and
message quality are inferential.

For CI/CD, YAML syntax and secret scanning are exact; diagnosis of a failed
deployment can require reasoning.

For research, citation structure and required sections are exact; source
relevance, coherence, and claim support require evidence-aware judgment.

### [Slide 7] Evaluator output is evidence, not truth — 5:35–6:15

Even a separately prompted evaluator can show position bias, prefer verbose
answers, or miss a subtle contradiction. Its finding does not become true
because it came from an “independent” model.

Preserve the raw finding, named criterion, cited evidence, and parser outcome.
Fail closed when required labels are missing. Audit a sample against human or
deterministic reference decisions. If the evaluator cannot meet the needed
false-acceptance rate, improve it, narrow its role, or escalate the decision.

### [Slide 8] Transition — 6:15–6:30

We now have an architecture and a measurable rubric. Next, we will connect them
into a bounded control loop that improves a candidate—or reports that it could
not.

## Domain comparison reference

| Domain | Deterministic evaluation | Inferential evaluation |
| --- | --- | --- |
| Coding | Tests, linting, typing | Design correctness, requirement satisfaction |
| SEO | Tag lengths, heading structure | Relevance, intent match, content quality |
| Marketing | Prohibited words, format rules | Brand voice, message quality |
| CI/CD | YAML syntax, secret scanning | Failure diagnosis, remediation quality |
| Research | Citation structure, required sections | Coherence, source relevance, claim support |

## Transition line

> A rubric tells us what to inspect. Loop engineering determines how those
> findings change the next attempt and when the system must stop.
