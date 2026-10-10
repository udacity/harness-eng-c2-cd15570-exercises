# Module 1 Demo: Five-Minute Instructor Script

## Before the demonstration

Confirm that the dependencies are installed and that `.env` contains a current
Vocareum `OPENAI_API_KEY`. Start in `module-1-evaluator/demo`.

Keep these files open in the editor:

1. `scenarios/inc_2048.json`
2. `harness/generator.py`
3. `harness/loops/basic_loop.py`
4. `harness/loops/self_evaluation_loop.py`
5. `harness/loops/external_evaluation_loop.py`
6. `main.py`

Live model responses vary. Describe the result that actually appears instead of
promising that a particular loop will pass or fail.

## 0:00–1:00 — Introduce the use case

**Show:** `scenarios/inc_2048.json`

**Say:**

> This demo begins with an incident ticket created outside the
> generator–evaluator loop. Production checkout failures increased after
> `checkout-v42`. The `checkout-api` is degraded, its error rate is 18 percent,
> and incident `INC-2048` is still being investigated.
>
> The ticket also tells us what has not happened. There has been no restart, no
> rollback, and no confirmed recovery. Those negative facts are important
> because an AI-generated update must not invent remediation or claim that the
> incident is resolved.
>
> The task is to produce a stakeholder update containing exactly 60 words, the
> correct incident ID, confirmed facts, and a useful diagnostic step before any
> production change. We will compare three ways of deciding when generation
> should stop.

**Point out:**

- The JSON ticket is authoritative input; the loop does not create it.
- A safe next step is investigation, such as checking logs and metrics.
- A rollback may be a future option, but the ticket does not say one occurred.

## 1:00–2:45 — Explain the code and the loops

**Show:** `harness/generator.py`

**Say:**

> All three modes use the same generator. It receives the authoritative incident
> facts, the operator request, and the response requirements. The first call has
> no `previous_response_id`, so it begins a fresh LLM conversation.

**Show:** `harness/loops/basic_loop.py`

**Say:**

> The basic loop generates an update and then asks for a clearer rewrite. It
> performs two cycles, but it never evaluates either answer. Its final status is
> `NOT CHECKED`. This is our baseline: repeating generation is not evidence that
> the result is correct.

**Show:** `harness/loops/self_evaluation_loop.py`

**Say:**

> The self-evaluation loop asks the generator to review its own answer in the
> same conversation. It checks four criteria and returns an explicit verdict. A
> failure produces feedback and another revision. A pass stops the loop.
>
> This is better than no evaluation, but the author and judge share the same
> conversation. The model may confidently miscount words or overlook one of its
> own unsupported claims.

**Show:** `harness/loops/external_evaluation_loop.py`

**Say:**

> The external loop gives us a stronger stopping boundary. Python checks exact
> requirements: the 60-word count and the incident ID. A fresh LLM conversation
> checks factual grounding and whether the next step is useful and safe.
>
> Both evaluation paths inspect the same candidate. The candidate is accepted
> only when every independent criterion passes. If self-review says pass while
> an independent check fails, the harness records a false positive instead of
> sending the update.

**Summarize the loop comparison:**

```text
basic:    generate → rewrite → stop without a quality decision
self:     generate → self-review → revise or trust the self-verdict
external: generate → Python checks + fresh review → revise or independently pass
```

## 2:45–5:00 — Run and narrate the demo

**Show:** the terminal in `module-1-evaluator/demo`.

**Run:**

```bash
python3 main.py compare
```

### At the initial scenario display

**Say:**

> The program first prints the authoritative ticket and response requirements.
> These are the facts against which every candidate should be judged.

### At the `BASIC loop ready` pause

Press Return.

**Say after its cycles:**

> The model produced two versions, but notice `Evaluation: NOT PERFORMED`. The
> loop stopped because it reached two cycles, not because anyone established
> that the response was correct. That is why the summary says `NOT CHECKED`.

### At the `SELF loop ready` pause

Press Return.

**Say after each self-review:**

> Here the same LLM conversation grades the candidate. If it fails, the feedback
> is used for the next revision. If it passes, this mode accepts the response.
> The displayed verdict is self-reported; it has not been independently proven.

If the self loop passes, say:

> The loop stopped because the model accepted its own work. We should read this
> as a claim from self-review, not as independent evidence of correctness.

If it reaches its attempt limit, say:

> Self-review did not produce an acceptable answer within the allowed cycles, so
> the harness stopped rather than continuing indefinitely.

### At the `EXTERNAL loop ready` pause

Press Return.

**Say after the first criteria table:**

> This table compares self-review with independent evidence for the exact same
> candidate. Word count and incident ID come from Python. Factual grounding and
> the next step come from a fresh evaluator conversation.

If `FALSE POSITIVE OBSERVED` appears, say:

> This is the key teaching moment. Self-review accepted the candidate, but an
> independent check found a real failure. The external loop therefore refused
> to stop on the model's unsupported pass.

If both paths agree, say:

> In this run the two paths agree. Live outputs vary, so a false positive is not
> guaranteed. The important difference is that the external decision has
> evidence outside the generator's self-review.

### At the final comparison table

**Say:**

> The final table does not rank writing style. It compares stopping rules.
> `NOT CHECKED` means generation stopped without evaluation. A self `PASS` means
> the model accepted its own work. An external `PASS` means every deterministic
> and inferential check passed; an external `FAIL` means the harness safely
> withheld acceptance.
>
> The takeaway is simple: a loop is only as trustworthy as its stopping
> condition. Exact requirements should be checked with code, and judgment-based
> requirements benefit from an evaluator outside the generator's conversation.

