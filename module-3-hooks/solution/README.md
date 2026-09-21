# Expense Report Agent: Hooks and Deterministic Antidotes

This runnable solution compares an expense agent with a policy prompt alone against the same agent with a before-tool policy hook.

## Use case

An employee asks an AI agent to review and submit an expense report. The agent sees the company's expense policy and can request the `submit_expense_report` tool. A report may look plausible while containing a duplicate receipt, an excessive meal, a missing approval, a nonpositive amount, or an incorrect total.

The exercise compares the **same agent and report** in two modes. In `basic`, the agent's tool request goes straight to a simulated submission tool. In `hooks`, the harness intercepts that request and applies the policy in Python before the tool can execute. The model receives the policy in both modes so it can review the report and explain the result.

| Mode | Path from model decision to tool | What it establishes |
| --- | --- | --- |
| `basic` | Model requests submission → harness executes the tool | The model reads the policy, but no code checks a proposed submission. |
| `hooks` | Model requests submission → before-tool hook checks the report → harness allows or blocks the tool | A proposed submission must pass deterministic checks before execution. |

The central distinction is **who controls execution**. The model chooses when to call a tool and when to answer. The harness handles each tool request, then returns its result to the model. A before-tool hook can block submission, but it does not choose the number of model cycles.

## Policy to enforce

The fictional company uses five exact rules:

1. Each meal expense must be **$100 or less**.
2. Any individual expense **over $500** requires manager approval. An expense of exactly $500 does not cross this threshold.
3. A receipt ID may appear only once in a report.
4. The reported total must equal the sum of all line-item amounts to the cent.
5. Every line-item amount must be greater than zero.

These rules are suitable for deterministic checks because the required facts are in the report and the pass or fail boundary is explicit. The exercise does not ask a hook to judge whether a meal is reasonable or a business justification is convincing.

Both modes give the model these five rules in the same system prompt. The user request contains only a report ID. `get_expense_report` returns the report header and numbered item indices, while `get_expense_item` returns one line item per call. The prompt asks the agent to inspect every item before proposing submission; a tool request is not itself a policy approval. The model can call tools again or give a final answer, so the cycle count depends on its responses.

A report has an `employee`, `report_id`, `manager_approved` flag, `reported_total`, and an `expenses` list. Each expense has a `receipt_id`, `category`, `description`, and `amount`. All three tools take a report ID; `get_expense_item` also takes a one-based item index. The harness resolves the ID to the original loaded report, which prevents the model from changing amounts or approval in the tool arguments. The before-tool hook checks that report immediately before submission.

## Hook, antidote, and tool

A **hook** is harness code that runs at a defined point in the agent loop. This exercise uses a `before_tool_call` hook immediately before `submit_expense_report` would execute. An **antidote** is one of the Python checks that prevents a known failure, such as submitting a $185 meal under a $100 limit.

The two retrieval tools expose report metadata and individual line items. The submission tool only simulates submission and returns a status and report ID. None of these tools contains the policy checks. The hook calls separate checks for positive amounts, meal limits, approval, duplicate receipts, and the reported total. It combines their findings into an allow or block result.

[`HookResult`](models.py) carries `allowed`, `violations`, and the pass or fail result of each check. The checks use ordinary Python and do not call an LLM. Money is compared as exact cents with `Decimal`, so the total rule does not depend on binary floating-point rounding.

```text
Agent calls get_expense_report(report_id)
                  |
                  v
       Agent receives item indices
                  |
                  v
Agent calls get_expense_item for each item it inspects
                  |
                  v
Model may call submit_expense_report(report_id)
                  |
                  v
       Harness loads original report
                  |
                  v
          before_tool_call hook
                  |
          five Python policy checks
             /            \
          PASS            BLOCK
           |                |
           v                v
      Execute tool    Return violations as
                      a tool result to model
```

When the hook blocks a call, the submission tool must **not** run. The harness returns the violations through the tool-result channel so the agent can explain them to the employee. A blocked tool result is still part of the agent conversation; the Python process does not stop at the hook. If all checks pass, the same submission tool executes and reports success.

Basic mode bypasses this hook entirely. It must not quietly validate the report in the tool or before the model call, because that would erase the comparison. Its summary should say violations were **not checked**, rather than reporting zero violations.

## Expense scenarios

The [`examples/`](examples) folder contains a valid report, a report with multiple violations, and a subtle `ambiguous` report. Both modes read the same selected JSON file. Direct Python checks can verify each antidote independently without changing a model response.

| Scenario | Key facts | Expected hook result if submission is requested |
| --- | --- | --- |
| `valid_expense` | Hotel $450, meal $85, taxi $55, conference registration $300; reported total $890; unique receipts; no approval needed. | All five checks pass; tool executes. |
| `multiple_violations` | Hotel $780 with no manager approval; meal $185; receipt `R002` repeated; five line items total **$1,712** but reported total is **$1,700**. | Approval, meal, duplicate, and total checks fail; tool does not execute. |
| `ambiguous` | Eight otherwise valid items add to $1,295.90, but the reported total is $1,295.89. | The total check fails by one cent; the hook blocks submission. |

The reported total in `multiple_violations` is deliberately $1,700. The line items add to $1,712; using $1,712 as the reported total would **not** exercise the total-mismatch rule. The `ambiguous` case is an ordinary input, with no hard-coded model mistake or edited model output.

The harness offers all three tools on each model call and does not force a specific call. It allows one tool call at a time, so the agent sees each result before choosing its next action. A response with a tool call starts another cycle after the tool result is returned. A response with a final answer ends the run. If the agent never requests submission, no before-tool hook runs; the summary reports `not_submitted`. When an invalid submission is requested, `basic` has no policy barrier, while `hooks` blocks it before execution. The valid scenario shows that hooks also allow actions that satisfy the rules.

## Run and compare

Run these commands from `module-3-hooks/solution/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
python3 main.py --mode basic
python3 main.py --mode hooks
python3 main.py --mode hooks --scenario valid_expense
python3 main.py --mode basic --scenario ambiguous
```

Without `--scenario`, both modes use `multiple_violations`. You can also pass `--scenario multiple_violations` explicitly. Compare the first two commands before trying another report.

Set `OPENAI_API_KEY` in `.env` to a Vocareum API key; `OPENAI_MODEL` may select the available model and defaults to `gpt-4.1-mini`. The harness uses the OpenAI Python SDK directly with the course's Vocareum endpoint. The submission tool is simulated and has no external side effect.

Compare modes using the same model, system prompt, user request, and expense JSON. Only the hook setting changes. The harness loops **until the model gives a final answer without a tool call**. The number of cycles is not fixed. On the five-item default report, a full inspection followed by submission and an answer takes about eight cycles: one report-header call, five item calls, one submission call, and the final answer. The agent can take a different path. After **each cycle**, the program prints `Cycle complete. Press Return to continue...`. Press Return to continue to the next model call or, after the final answer, to the run summary. Time spent waiting for Return is excluded from `Model seconds`. A 24-cycle safety limit raises an error if the model never finishes; it does not manufacture a final answer.

Each run writes a timestamped log in `output/`. The log shows the proposed tool call, whether the before-tool hook ran, each check's result, whether the tool executed, and the agent's final response. The summary includes:

```text
Mode:                 hooks
Tool calls:           7
Report retrieved:     yes
Items inspected:      5/5
Submission requested: yes
Hook executed:        yes
Violations detected:  4
Submission executed:  no
Final status:         blocked
Model cycles:         8
```

For `basic`, the summary reports `Hook executed: no` and `Violations detected: not checked`. If the agent finishes without requesting submission, it reports `Hook executed: no` and `Final status: not_submitted`. Token counts and model time are also displayed.

## Questions for the exercise

1. Why does putting the expense policy in the system prompt differ from enforcing it with a hook?
2. Which expense rules are appropriate for deterministic checks?
3. Which expense decisions might still require judgment from a person or model?
4. Why must validation run before submission instead of after it?
5. What happens if the model answers without requesting submission?
6. What happens if the model overlooks a violation and requests submission?
7. Should every model decision have a deterministic hook? Why or why not?
8. How could the same hook pattern be reused for another tool?

## What to inspect

- [`agent.py`](agent.py) contains the model and tool loop, the Return pause, and the `basic`/`hooks` switch.
- [`hooks.py`](hooks.py) contains `before_tool_call` and five deterministic policy checks.
- [`tools.py`](tools.py) contains report-header retrieval, item retrieval, and simulated submission, with no policy logic.
- [`main.py`](main.py) loads the scenario and prints the execution summary.
- [`run_log.py`](run_log.py) copies terminal output into a run log.

## File map

```text
solution/
├── main.py                 # CLI, scenario loading, and run summary
├── agent.py                # shared model and tool loop; optional hook call
├── tools.py                # report and item retrieval; simulated submission
├── hooks.py                # before-tool hook and five Python checks
├── models.py               # small hook-result structure
├── run_log.py              # per-run terminal log
├── examples/               # valid, invalid, and subtle reports
├── .env.example
├── requirements.txt
└── README.md
```
