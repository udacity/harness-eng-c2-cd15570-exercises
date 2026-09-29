# Module 1 Demo: Evaluating an Incident Update

This is the first demo in the shared incident-response sequence. A fictional
production `checkout-api` is degraded after deployment `checkout-v42`. The
agent must draft an accurate update for incident `INC-2048` without claiming
that an unobserved rollback, recovery, or resolution occurred.

The demo compares three generator–evaluator loops over the same authoritative
incident state and response requirements:

| Mode | Flow | What it demonstrates |
| --- | --- | --- |
| `basic` | Generate → request a clearer rewrite → stop | More cycles do not establish quality. |
| `self` | Generate → evaluate in the same conversation → revise on failure | A generator can judge its own response, but may share its original mistake. |
| `external` | Generate → self-review and independently evaluate the same candidate → revise on independent failure | Deterministic checks and a fresh evaluator provide a separate stopping boundary. |

There are no business tools, skills, hooks, or enforced permissions yet. The
trusted user is displayed to establish the shared course context; authorization
is introduced in the Module 4 demo.

## Shared incident

The immutable scenario is in [`scenarios/inc_2048.json`](scenarios/inc_2048.json):

```text
Incident:               INC-2048
Environment:            production
Service:                checkout-api
Current deployment:     checkout-v42
Last-known-good:         checkout-v41
Service health:         DEGRADED
Checkout error rate:    18%
Rollback performed:     false
Recovery confirmed:     false
Authenticated user:     Sam Rivera, support_engineer
```

The generator must write exactly 60 words, include `INC-2048`, use only confirmed
facts, avoid unsupported action or recovery claims, and provide a useful next
diagnostic step.

## Run the reliable classroom demo

The default provider is a deterministic scripted fixture and requires no API
key or package installation:

```bash
cd module-1-evaluator/demo
python3 main.py compare
```

The scripted initial response falsely says the incident was resolved and a
rollback succeeded. In `self`, the scripted reviewer first returns `FAIL`, the
generator revises from that review response, and the second review passes. In
`external`, self-review incorrectly returns `PASS` for the flawed first draft;
Python checks and a fresh inferential review inspect that exact candidate,
report the false positive, and drive a corrected second response.

Run a single mode when presenting one stage:

```bash
python3 main.py basic
python3 main.py self
python3 main.py external
```

Add `--pause` to stop after every cycle. Every run writes the complete terminal
output to a timestamped file under `output/`.

## Run with a live model

Install the dependencies and create a local environment file:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Add your course API key to `.env`, then run:

```bash
python3 main.py compare --provider live
```

Override the configured model when needed:

```bash
python3 main.py external --provider live --model gpt-4.1-mini
```

The default endpoint is `https://openai.vocareum.com/v1`; it can be changed
with `OPENAI_BASE_URL`. `.env` and run logs are ignored by Git.

Live outputs vary. A good initial response may pass independently, and a
self-evaluation false positive may not occur. Compare self and independent
results only within the `external` mode because both evaluators inspect the
same candidate there. Separate `self` and `external` runs generate different
live drafts.

## Evaluation boundary

Python performs the criteria that do not need model judgment:

- the exact `INC-2048` identifier is present; and
- `len(candidate.split()) == 60`.

A fresh evaluator judges:

- factual grounding against the complete authoritative snapshot; and
- whether the proposed next step is useful and safe.

Missing or malformed named decisions fail closed. The external decision passes
only when both Python checks and both inferential criteria pass. Inferential
evaluation can still be wrong, so the terminal shows the candidate, raw review,
and criterion comparison rather than hiding them behind one score.

## Conversation boundaries

The loops call `client.responses.create(...)` directly, just as the exercise
does. The terminal prints the exact continuation rule at every stage:

```text
Initial generation: no previous_response_id
Self-review:        previous_response_id=candidate.id
Self revision:      previous_response_id=self_review.id
External review:    no previous_response_id
External revision:  previous_response_id=candidate.id
```

The self revision continues through the review because that review belongs to
the generator conversation. The independent evaluator starts fresh so it does
not inherit the generator's reasoning. External feedback returns to the
candidate branch rather than continuing the evaluator's separate conversation.

## Deterministic tests

The tests use only the scripted provider and require no API key:

```bash
python3 -m unittest discover -s . -p 'test_*.py'
```

They verify the stable incident contract, exact Python checks, fail-closed
result parsing, basic loop semantics, the intentional self-review false
positive, review of the same candidate, every `previous_response_id` boundary,
feedback-driven revision, and the external stopping decision.

## What to show during the demo

1. Point out that the incident state says no rollback or recovery occurred.
2. Run `basic` and show that a clearer rewrite can remain false.
3. Run `self` and show that `PASS` comes from the same conversation.
4. Run `external` and confirm that both review paths receive the same candidate.
5. Follow the independent feedback into the corrected response.
6. End on the comparison table: loop completion and response quality are not
   the same measurement.

The scripted false positive is deliberately guaranteed so this teaching moment
is reliable. It is not a prediction about the exercise. Exercise runs use live
model output, and students must report the result they observe rather than
altering inputs to manufacture a disagreement.

## From this demo to the exercise

The domain changes from an incident update to customer-support replies, but the
implementation task has the same shape:

| Demo code | Exercise task |
| --- | --- |
| `passed()` | Parse an explicit self-evaluator `VERDICT`, failing closed when absent. |
| `evaluate_own_response()` | Continue the generator conversation with `previous_response_id=response.id`. |
| `evaluate_deterministic_criteria()` | Count words with `split()` and find the exact case identifier in Python. |
| `evaluate_inferential_criteria()` | Start a fresh evaluator conversation for the judgment-based criteria. |
| `run_self_evaluation_loop()` | Review, revise from the review response, and stop on self `PASS` or the limit. |
| `run_external_evaluation_loop()` | Evaluate the same candidate on both paths, compare criteria, revise from external feedback, and stop on independent `PASS` or the limit. |

In the exercise, the exact deterministic requirement is 100 words rather than
60, `CASE-####` replaces `INC-####`, and five cases are processed. The
evaluator boundaries and loop responsibilities remain the same.

## Repository map

```text
demo/
├── main.py                    # CLI, provider setup, summaries, and logging
├── harness/
│   ├── clients.py             # scripted client and live timing adapter
│   ├── generator.py           # shared prompt and initial Responses API call
│   ├── loops/
│   │   ├── basic_loop.py
│   │   ├── self_evaluation_loop.py
│   │   └── external_evaluation_loop.py
│   ├── models.py              # evidence structures
│   ├── results.py             # token, time, and run summaries
│   ├── run_log.py             # timestamped terminal log
│   └── scenario.py            # scenario loading and prompt context
├── scenarios/
│   └── inc_2048.json          # shared incident facts and requirements
├── test_demo.py
├── .env.example
└── requirements.txt
```

Module 2 will keep the same incident and evaluator boundary while adding
selective incident-response skills.
