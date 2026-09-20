# Generator–Evaluator Harness: Solution

## Call center use case

You are responsible for checking the replies drafted by a customer-support agent at a fictional call center. Each customer case describes a purchase, a product problem, and a requested resolution. The agent must write a helpful response that follows the supplied refund and replacement policy. For example, if a customer requests a refund 45 days after purchase, the agent may offer a replacement or escalate the request, but it cannot promise a refund.

The solution harness generates drafts for five customer cases and checks whether each response has exactly 100 words, includes the case ID, follows the policy, and offers a useful next step. Run its three modes to see how the choice of evaluator changes the feedback and the stopping decision.

## Exercise objective

Run the modes in order and inspect what happens to each response:

1. Run `basic` to see a first draft and a clearer revision for each case. The loop makes no quality judgment, so reaching its two-cycle limit says nothing about whether a response meets the requirements.
2. Run `self` to see the model review its own draft in the same conversation. Note when it returns `PASS` and when it catches a problem and requests a revision. Self-review may pass most drafts in a run, but its `PASS` is still an unverified judgment.
3. Run `external` to compare self-review with checks of the **same draft**. Look for `FALSE POSITIVE OBSERVED`: self-review gave an overall `PASS`, while an independent check found an error. Follow the feedback into the next cycle to see whether the generator corrects it.

Live model responses vary. A run may show different numbers of self-review failures and false positives, including none.

## Why these customer cases?

The [refund and replacement policy](data/reference/refund_policy.md) depends on when the customer purchased the product, whether they have proof of purchase, and whether the product is defective. Customers may also ask the agent to make a promise the policy does not allow. The five cases put those decisions into realistic support conversations so you can see whether the generator applies the policy and whether either evaluator catches a mistake. A customer's request, including any requested wording, is part of the case and does not override the policy.

All five customer cases, including the original CASE-1842, are in [data/cases](data/cases). The runner loads every Markdown file in that folder for each run.

| Case | Situation | What the response needs to handle |
| --- | --- | --- |
| [CASE-1842](data/cases/case_1842_refund_window.md) | Two defective devices of the same model have receipts dated 31 and 29 days ago; the customer wants both refunded together. | The agent must apply the refund window to each device separately. The newer device can qualify for a refund; the older one can qualify for replacement or refund escalation. |
| [CASE-2091](data/cases/case_2091_manager_promise.md) | A customer claims a manager already approved a refund for a working product purchased 47 days ago and asks when the money will arrive. | The agent cannot verify the claimed approval or promise a payout date. The case tests whether treating confirmation as different from approval leads to an out-of-policy promise; escalation is a possible next step. |
| [CASE-3175](data/cases/case_3175_delivery_date.md) | A defective product was purchased 31 calendar days ago and delivered 9 days ago. As in CASE-2091, the customer claims a manager approved a refund and asks support to confirm it and give a payout date. | The refund limit is **30 calendar days from purchase**. The claimed approval is unverified; the agent can offer replacement or escalation without confirming a refund or payout date. |
| [CASE-4420](data/cases/case_4420_customer_pressure.md) | A defect appeared on day 89, but the customer first requests help on day 91 and argues that replacement is still available. | The request is outside the 90-day replacement window. The agent must avoid promising either a replacement or a refund; escalation is available for the refund request. |
| [CASE-5683](data/cases/case_5683_missing_proof.md) | The customer supplies a recent receipt for a different product and claims it proves the overheating product was purchased 22 days ago. | The receipt does not establish purchase of the product at issue. The agent should seek matching proof or order details before approving a refund. |

Together, the cases place a plausible but misleading fact next to the fact that controls the policy decision. CASE-2091 and CASE-3175 also test whether an unverified manager claim makes the agent confirm an out-of-policy refund. A response can sound complete while applying one rule to both devices, counting the wrong kind of days, using defect onset instead of request timing, or accepting proof for the wrong item. Self-review may share the generator's mistaken assumption and approve that response; the independent evaluator checks the candidate against the policy and case in a separate conversation. Live verdicts still vary, so no case guarantees a failure.

## What the harness does

This solution demonstrates how a harness changes the way those responses are reviewed. The harness controls which documents the model receives, when it asks for another response, who evaluates that response, and when the loop stops. Its three run modes use the same policy, response requirements, and customer cases. They progress from a basic revision loop to self-evaluation and then independent evaluation. There are no agent tools or skills in this exercise.

## The three run modes

| Mode | Flow | What it demonstrates |
| --- | --- | --- |
| `basic` | Generate → ask for a clearer revision → stop after two cycles | Repeating a model call does not verify quality. |
| `self` | Generate → review in the same conversation → revise on `FAIL` → stop on `PASS` or after at most two cycles | The agent judges its own response with access to its prior conversation. |
| `external` | Generate → compare self-review, Python checks, and a fresh model review of the **same response** → revise on external `FAIL` | Checks outside the generator conversation can find missed errors and guide a correction, up to three cycles. |

The self-evaluator is a separate API call that continues the generator's conversation with `previous_response_id`. The fresh evaluator is also an API call, but it starts a new conversation with its own instructions and receives only the policy, case, requirements, and candidate response. Both calls use the configured model by default; *independent* here means separate prompt and conversation, not necessarily a different model. In `external`, Python separately checks the word count and case ID.

The `self` mode's default limit is **two cycles per case**. Each cycle generates a response and reviews it: the first uses the initial draft, and a second runs only if the first review fails. If the revised response also fails, the loop reports that it reached the limit and moves to the next case. The count resets for each customer case. To allow more attempts, change `max_attempts: int = 2` in [`run_self_evaluation_loop`](harness/loops/self_evaluation_loop.py) to a higher number, such as `4`. That allows the initial draft plus up to three revisions; the loop still stops early when self-review passes. `main.py` calls the function with its default value, so changing that default changes `python3 main.py self`.

## The task and evaluation criteria

The source documents are [data/reference/refund_policy.md](data/reference/refund_policy.md) and [data/reference/response_requirements.md](data/reference/response_requirements.md). Both are in the `data/reference/` folder.

The fictional refund policy allows a full refund within 30 calendar days when proof of purchase is available. After 30 days, a support agent cannot approve or promise a refund. A defective product can qualify for replacement within 90 days, and an out-of-policy refund request can be escalated without guaranteeing approval.

The response requirements document defines four checks:

| Type | Criterion | How the solution checks it |
| --- | --- | --- |
| Deterministic | Exactly 100 whitespace-separated words | Python counts the words with `split()`. |
| Deterministic | Includes the case's exact `CASE-####` ID | Python checks for that ID. |
| Inferential | Follows the refund and replacement policy | A fresh evaluator conversation judges the response. |
| Inferential | Gives a useful, policy-compliant next step | The fresh evaluator judges the response. |

The exact count creates an objective check that the model may misjudge when reviewing its own draft. In `external`, the Python count and the self-review apply to the **same response**. If self-review gives an overall `PASS` but Python counts anything other than 100 words, the comparison reports a self-evaluation false positive. The policy and next-step checks remain model judgments, so inspect the response when those evaluators disagree.

## Set up

From `module-1-evaluator/solution-evaluator`, install the dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Create `.env` from [.env.example](.env.example) if it does not already exist. Add your Vocareum API key and a model available to your account:

```dotenv
OPENAI_API_KEY=your-vocareum-api-key
OPENAI_MODEL=gpt-4.1-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4.1-mini`. [main.py](main.py) loads `.env`, creates an OpenAI Python client, and routes requests through `https://openai.vocareum.com/v1`. Git ignores `.env`; keep your real key there rather than in source files.

## Run the loops

Run these commands from the `solution-evaluator` directory. Each command processes all five cases and prints the policy, requirements, case, model output, and relevant loop stages.

```bash
python3 main.py basic
python3 main.py self
python3 main.py external
```

Each command runs the selected mode on all five files in `data/cases/`. The message `COMPLETED 5 CUSTOMER CASES` counts those files; a cycle is one attempt within a case. In `basic`, each case has two cycles, so a full run has ten cycles across five cases. The program pauses after every cycle and after every case. Press Return at each prompt to continue.

Each run also saves its terminal output, including prompts and errors, to a new file in `output/` named for the mode and UTC start time, such as `output/external-20260920T153000.000000Z.log`. The first terminal line prints the exact path. These run logs are ignored by Git.

Use `python3 main.py --help` to list the modes. Each mode makes live model requests, so the exact responses and verdicts can vary between runs.

Start with `basic` to see two customer responses per case: the first draft and a clearer revision. There is no evaluator or quality-based stop condition. Then run `self` to see whether the model accepts its own response or asks itself to revise it. Its self-review takes place in the generator's conversation and can return either `PASS` or `FAIL`; a `PASS` there has not been checked independently.

Run `external` to compare the two evaluation paths and correct failed responses. In each cycle, self-review, Python, and the fresh evaluator inspect the **same generated response**. The terminal shows their verdicts side by side for all four criteria:

```text
Criterion          | Self | Independent
-------------------+------+------------
WORD_COUNT         | PASS | FAIL
CASE_ID            | PASS | PASS
POLICY_COMPLIANCE  | PASS | PASS
USEFUL_NEXT_STEP   | PASS | PASS

FALSE POSITIVE OBSERVED: Self-evaluation passed a flawed response.
```

The `Independent` column combines Python's `WORD_COUNT` and `CASE_ID` results with the fresh model's `POLICY_COMPLIANCE` and `USEFUL_NEXT_STEP` judgments. The displayed `Independent evaluator verdict` passes only when all four checks pass. The fresh model may mention word count in its prose, but Python's count determines the `WORD_COUNT` result.

`FALSE POSITIVE OBSERVED` means the self-evaluator returned an overall `PASS` while at least one check in the `Independent` column returned `FAIL` for that **same response**. A `PASS` in a separate `self` run and a `FAIL` in an `external` run are not directly comparable because those runs generate different responses. The fresh model's policy and next-step judgments can also be wrong; inspect the response and policy before treating a disagreement as a confirmed policy mistake.

When the independent checks fail, `external` sends their feedback back to the generator for a revision. The loop stops when all four criteria pass or after three attempts. Its final summary counts cases where it observed a self-evaluation false positive.

No individual live run is guaranteed to reproduce a false positive. If the model produces valid responses, or if self-review catches every error, the summary will report zero observed false positives. That is an honest result of this experiment.

## Where the behavior lives

| File | Responsibility |
| --- | --- |
| [main.py](main.py) | Loads `.env` and exercise data, selects a mode, and prints the run summary. |
| [harness/run_log.py](harness/run_log.py) | Copies terminal output to a per-run log file. |
| [harness/pauses.py](harness/pauses.py) | Prompts for Return after every cycle and case. |
| [harness/generator.py](harness/generator.py) | Builds the customer-support prompt and makes the initial model request. |
| [harness/loops/basic_loop.py](harness/loops/basic_loop.py) | Runs the fixed two-cycle revision loop. |
| [harness/loops/self_evaluation_loop.py](harness/loops/self_evaluation_loop.py) | Reviews a response in the generator's conversation. |
| [harness/loops/external_evaluation_loop.py](harness/loops/external_evaluation_loop.py) | Compares both reviews of one response, runs independent checks, and sends feedback for revision. |
