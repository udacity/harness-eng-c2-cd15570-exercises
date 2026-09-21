# Generator–Evaluator Harness: Student Exercise

## The use case

A fictional call center uses an AI assistant to draft replies to customers asking about refunds and replacements. Each reply must handle the customer's circumstances, follow the call center's policy, and give a useful next step. A polished reply can still be wrong: it may promise an unauthorized refund, accept a receipt for the wrong product, omit the case ID, or miss an exact word limit.

The supplied [refund and replacement policy](data/reference/refund_policy.md) and [response requirements](data/reference/response_requirements.md) define the task. The five files in [data/cases](data/cases) supply customer requests. The cases include boundary dates, claimed manager approval, customer pressure, and mismatched proof of purchase. They give you concrete responses to inspect as you change how the harness evaluates a draft. The runner processes **all five cases** each time you select a loop.

## Exercise objective

Build and compare three loops that solve the same customer-support task:

| Mode | What you should observe |
| --- | --- |
| `basic` | The supplied loop generates a reply, asks for a clearer revision, and stops after two cycles without checking quality. |
| `self` | Your loop asks the model to review its own reply in the **same conversation**. It can catch an issue and request a revision, but a `PASS` is only the model's judgment. |
| `external` | Your loop compares self-review with checks of the **same draft** made outside the generator conversation. Python checks exact rules; a fresh model conversation judges policy compliance and the next step. External feedback drives revision. |

In your run notes, show whether self-review accepted most drafts and identify any failures it caught. Then look for a draft that self-review passed while an external check failed. If one appears, explain the error and show the check that caught it. Live model output varies, so a particular number of passes or false positives is not guaranteed. A run with none is still a valid observation; do not edit case files or logs to manufacture one.

## The response criteria

Read both documents in `data/reference/` before coding. Every customer reply must:

1. Contain **exactly 100 words**, counted by splitting on whitespace.
2. Include the exact `CASE-####` ID from its customer case.
3. Follow the [refund and replacement policy](data/reference/refund_policy.md), without approving or promising a refund the agent cannot authorize.
4. Give a useful, policy-compliant next step, such as an eligible replacement or escalation to a billing specialist.

The first two checks have exact answers that Python can calculate. The last two require judgment against the policy and case. In `external`, keep the fresh model focused on those last two checks; its prose about the word count must not override Python's count.

## What is supplied and what you add

The starter includes the five cases, both reference documents, model setup, generation prompt, terminal logging, Return-to-continue pauses, and a complete `basic` loop. The CLI in [main.py](main.py) already selects `basic`, `self`, or `external`. The `self` and `external` modules contain TODOs and raise `NotImplementedError` until you implement them, as in the project starter.

Work through these files in order:

1. **[harness/loops/self_evaluation_loop.py](harness/loops/self_evaluation_loop.py):** Write a reviewer prompt covering all four criteria and a clear `VERDICT`. Parse that verdict, failing closed when it is absent. Call `client.responses.create` with `previous_response_id=response.id` so the review continues the generator's conversation. Implement the two-cycle loop: print the draft and review, stop on self `PASS`, and otherwise revise from the review response ID. Pause after every cycle.
2. **[harness/loops/external_evaluation_loop.py](harness/loops/external_evaluation_loop.py):** Check `len(candidate.split()) == 100` and the exact case ID in Python. Write a fresh evaluator prompt for policy compliance and useful next step, then call the model **without** `previous_response_id`. Parse its two named results. Compare its results and Python's results with the self-review of the **same candidate**; report a false positive when self-review says overall `PASS` and at least one external check says `FAIL`. Revise using external feedback, stopping when all four external checks pass or after three cycles. Pause after every cycle.

Keep the candidate unchanged while all reviewers inspect it. A separate `self` run and `external` run generate different replies, so their verdicts cannot demonstrate a false positive against one draft. The comparison inside an `external` cycle can.

The supplied cases and reference documents are exercise inputs. Keep them intact so the three modes receive the same task.

## Set up

Use Python 3.12 or a compatible Python 3 installation. From `module-1-evaluator/exercise-evaluator/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and replace the example key with your Vocareum API key:

```dotenv
OPENAI_API_KEY=your-vocareum-api-key
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`. The supplied code uses the OpenAI Python client with `https://openai.vocareum.com/v1`. `.env` and generated logs are ignored by Git; keep your real key out of source files and run evidence.

## Run and inspect the loops

Start with the working foundation:

```bash
python3 main.py basic
```

After completing the TODOs in each later module, run:

```bash
python3 main.py self
python3 main.py external
```

The program prints the policy, requirements, and each customer case before processing it. One **cycle** is one draft and its review or revision step for one case. The message `COMPLETED 5 CUSTOMER CASES` counts case files, not cycles. `basic` always uses two cycles per case; `self` allows up to two; `external` allows up to three. The limits reset for each case. To try a higher limit, change the `max_attempts` default in the relevant loop function. Press **Return** after every cycle and after every case to continue.

Each run saves everything printed to the terminal, including errors, in a new `output/<mode>-<UTC timestamp>.log` file. The first line prints its full path. Inspect the log after a run so you can cite the exact candidate, its self verdict, and the external results in your explanation.

For an external false positive, your output should make the comparison visible:

```text
Criterion          | Self | Independent
-------------------+------+------------
WORD_COUNT         | PASS | FAIL
CASE_ID            | PASS | PASS
POLICY_COMPLIANCE  | PASS | PASS
USEFUL_NEXT_STEP   | PASS | PASS

FALSE POSITIVE OBSERVED: Self-evaluation passed a flawed response.
```

Here, **Independent** means the combined external verdict: Python supplies `WORD_COUNT` and `CASE_ID`, and a fresh model conversation supplies `POLICY_COMPLIANCE` and `USEFUL_NEXT_STEP`. A separate model conversation can also make mistakes, so inspect the policy and candidate when model judgments disagree. The exact Python checks provide the strongest evidence for a missed word-count or case-ID error.

## Completion check

- [ ] `basic` runs on all five cases and stops at its fixed cycle limit without claiming to evaluate quality.
- [ ] `self` prints a review for each draft, revises on `FAIL`, and stops on `PASS` or its two-cycle limit.
- [ ] `external` runs the two Python checks and fresh model review on the same draft that self-review saw.
- [ ] `external` prints the four-criterion comparison, records any observed self-review false positive, and revises from external feedback.
- [ ] Your run notes cite the saved logs and explain what each loop's stopping decision does and does not establish.

## Repository map

```text
exercise-evaluator/
├── data/
│   ├── cases/                  # five supplied customer cases
│   └── reference/              # refund policy and response requirements
├── harness/
│   ├── generator.py            # supplied task prompt and first model call
│   ├── pauses.py               # supplied cycle and case pauses
│   ├── run_log.py              # supplied terminal-to-file logging
│   └── loops/
│       ├── basic_loop.py        # supplied working loop
│       ├── self_evaluation_loop.py      # student TODOs
│       └── external_evaluation_loop.py  # student TODOs
├── main.py                     # supplied CLI and case loading
├── .env.example
├── requirements.txt
└── README.md
```
