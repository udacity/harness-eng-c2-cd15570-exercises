# Module Overview

## Module identity

- **Course capability:** C2.1 — Loop Engineering in the Harness
- **Exercise:** I2.1 — Generator–Evaluator Separation
- **Audience:** software developers and AI engineers building agentic systems
- **Target duration:** approximately 32 minutes across five videos
- **Running example:** an AI-generated stakeholder update for incident
  `INC-2048`

## Why this module exists

A model can produce an answer that sounds complete while violating an exact
requirement, contradicting evidence, or omitting the requested outcome. Asking
the same conversation whether it did a good job may help in some cases, but it
does not create independent evidence. The generation path and its review can
share assumptions, context, and blind spots.

This module moves acceptance authority into the harness. Students learn to
separate the candidate author from the acceptance mechanism, combine exact and
judgment-based checks, bound revisions, and measure whether evaluation earns
its cost.

The position is deliberately balanced:

- self-review can improve outputs;
- independent evaluation can also be wrong;
- separate roles reduce one source of correlated error but do not eliminate
  bias;
- deterministic verification is preferred when the requirement is directly
  computable; and
- production claims require representative evidence rather than confidence.

## Lesson sequence

| Video | Title | Duration | Central question |
| --- | --- | ---: | --- |
| 1 | When agents judge their own work | 6:00 | Why is confidence not verification? |
| 2 | Separate the generator from the evaluator | 6:15 | Which component should own acceptance? |
| 3 | Deterministic and inferential criteria | 6:30 | How do we turn “good” into measurable checks? |
| 4 | Engineer the evaluation loop | 7:00 | How should feedback, retries, budgets, and failure work? |
| 5 | Measure whether the evaluator helps | 6:15 | Did quality improve enough to justify cost and latency? |

**Total target duration:** 32 minutes.

## Narrative arc

### Act 1: Expose the failure

Begin with a deliberately flawed incident update that claims a rollback and
recovery not present in authoritative state. A same-conversation review accepts
it in the scripted illustration. The lesson distinguishes an answer that looks
finished from a task whose requirements have been verified.

### Act 2: Move authority into the harness

Introduce three roles:

```text
generator -> candidate
evaluator -> structured findings
controller -> accept, retry, escalate, or stop
```

The evaluator receives the original requirement and relevant evidence, not
just the generator's explanation of what happened.

### Act 3: Define success precisely

Use exact Python checks for the incident ID and 60-word requirement. Use an
independent evaluator for factual grounding and usefulness of the next step.
Make every result explicit and fail closed on malformed evaluator output.

### Act 4: Bound the loop

Return actionable findings to the generator, re-evaluate the revision, and stop
only on complete acceptance or a declared limit. A limit reached without a pass
is a reported failure, not “best effort success.”

### Act 5: Demand evidence of value

Compare self and independent evaluation on the same cases against an external
reference standard. Report false acceptance, false rejection, improvement,
iterations, tokens, latency, and cost. Keep an evaluator only when its measured
benefit supports the operational tradeoff.

## Architecture taught

```text
request + evidence
        |
        v
    generator ---------> candidate
                            |
             +--------------+--------------+
             |                             |
             v                             v
    deterministic checks          inferential evaluator
             |                             |
             +--------------+--------------+
                            v
                    structured findings
                            |
                            v
                   harness controller
                  /        |          \
              accept      retry      escalate/fail
```

## Scope

The target architecture includes:

- separate generator and evaluator calls;
- independent prompts and conversational contexts;
- at least five measurable criteria;
- deterministic and inferential checks;
- structured findings with evidence;
- bounded revision iterations;
- quality, cost, and latency measurement;
- failure logging and human escalation; and
- optional cross-model evaluation.

## Deliberate non-goals

- Training a GAN or claiming the loop is a GAN.
- Proving that self-evaluation always fails.
- Treating an LLM evaluator as ground truth.
- Building a large autonomous incident-response platform.
- Hiding evaluator errors behind one aggregate score.
- Optimizing prompts before defining acceptance evidence.

## Exercise alignment

The first hands-on exercise concentrates on inferential evaluation so students
can observe the difference between same-conversation review and a fresh
evaluation call. The course then layers in exact checks, multiple criteria,
bounded retries, cost accounting, and failure evidence. The customer-support
exercise changes the business domain but preserves the same responsibility
boundaries.

## Completion evidence for the module

Students should leave with artifacts, not just vocabulary:

1. a generator prompt;
2. a separate evaluator prompt;
3. an explicit rubric;
4. at least two deterministic checks;
5. structured evaluator output;
6. controller pseudocode with bounded retries;
7. one recorded failed run that does not claim success; and
8. a comparison showing quality and cost against an external reference.
