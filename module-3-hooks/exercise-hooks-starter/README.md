# Expense Report Hooks: Student Exercise

## The use case

An employee wants an agent to review and submit an expense report. The agent can retrieve the report header, inspect numbered expense items, and request submission. The [examples](examples) include a valid report, one with several violations, and one with a one-cent total error.

The harness compares two modes using the same model, prompt, report, and tools:

| Mode | Submission behavior |
| --- | --- |
| `basic` | The supplied baseline executes a proposed submission without checking expense policy in Python. |
| `hooks` | Your before-tool hook checks the original report and either permits or blocks submission. |

The agent chooses which tool to call next. A model response with a tool call starts another cycle; a final answer ends the run. There is **no scripted number of cycles**. `get_expense_report` returns only the report header and item indices, and `get_expense_item` returns one item per call. A full review of the five-item default report followed by submission and an answer takes about eight cycles, but model behavior can differ. Press **Return after every cycle**, including the final one.

## Expense policy

Implement these five exact rules in Python:

1. Every line-item amount must be greater than zero.
2. Each meal expense must be **$100.00 or less**.
3. An individual expense **over $500.00** requires manager approval. Exactly $500.00 does not.
4. Receipt IDs must be unique within a report.
5. The reported total must equal the sum of the line items **to the cent**.

The model sees the policy, but its judgment is not the execution gate. The before-tool hook runs only when it proposes `submit_expense_report`. Retrieval calls never need the policy hook. Use `Decimal` for money checks, and reject malformed values rather than letting them pass.

## What is supplied and what you build

The starter supplies three expense scenarios, the report retrieval and simulated submission tools, model setup, a working `basic` loop, Return pauses, run logging, and the `HookResult` structure. The `hooks` mode raises `NotImplementedError` when the agent proposes submission until you complete the TODOs. The supplied [test_hooks.py](test_hooks.py) exercises the policy checks without an API key; it fails until you implement them.

Work through these files:

1. **[hooks.py](hooks.py):** Implement `_money` so policy checks use finite dollar amounts with at most two decimal places. Reject booleans, invalid strings, nonfinite numbers, and fractions of a cent.
2. **[hooks.py](hooks.py):** Implement all five checks. Return useful findings that identify the expense or total involved. Pay attention to exact boundary values and to duplicate IDs later in the list.
3. **[hooks.py](hooks.py):** Implement `validate_expense_submission`. Reject malformed report shapes, run **every** check, populate `HookResult.checks`, collect all violations, and allow submission only when every check passes.
4. **[hooks.py](hooks.py):** Implement `before_tool_call`. Accept only `submit_expense_report` and validate the original report provided by the harness. An unknown tool or malformed arguments must be blocked.
5. **[agent.py](agent.py):** Complete the `hooks` branch in `_tool_result`. Call the hook **before** the submission tool. On block, return violations as a `function_call_output` and leave the submission tool uncalled. On allow, execute the same submission tool used in `basic`. Record and print each check's result so the log shows what happened.
6. **[agent.py](agent.py):** Implement `count_failed_rules` for the run summary. Count distinct failed policy checks; an allowed submission reports zero. Handle malformed reports blocked before individual checks could run.
7. **Your experiment:** After the supplied scenarios work, add `examples/thresholds.json` with a $100 meal and a $500 expense without manager approval. Set an exact matching total. Run it in `hooks`, then change one threshold by one cent and explain the changed hook decision. Keep the three supplied examples intact for the first comparison.

The shared `while` loop, tool-result handoff with `previous_response_id`, and Return pause are supplied. Follow the tool request and result through that loop while adding the hook at the execution boundary. The summary distinguishes a requested submission from one that actually executed.

## Set up

Use Python 3.12 or a compatible Python 3 installation. From `module-3-hooks/exercise-hooks-starter/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Put your Vocareum API key in `.env`. `OPENAI_MODEL` defaults to `gpt-4.1-mini`. The code uses the OpenAI Python client with `https://openai.vocareum.com/v1`. `.env` and generated `output/` logs are ignored by Git.

## Run and inspect

Start with the supplied baseline:

```bash
python3 main.py --mode basic --scenario multiple_violations
```

Run the checks while you implement the hook:

```bash
python3 -m unittest test_hooks.py
```

Then compare the same report in both modes and try the other scenarios:

```bash
python3 main.py --mode hooks --scenario multiple_violations
python3 main.py --mode hooks --scenario valid_expense
python3 main.py --mode hooks --scenario ambiguous
```

`multiple_violations` is the default when `--scenario` is omitted. Each run saves a timestamped `output/` log. Compare the tool sequence, item count, model cycles, hook checks, submission status, final answer, tokens, and model time. The time spent waiting for Return is excluded from model time. A 24-cycle safety limit raises an error if the model never produces a final answer; it does not create a final answer for the model.

Live model behavior varies. It may answer before requesting submission, in which case the hook does not run. Explain what happened using the log; do not report that an uncalled hook passed. A blocked tool request should still be returned to the agent so it can explain the violations.

## Completion check

- [ ] `basic` still runs through the supplied agent-driven loop with no Python policy check.
- [ ] The hook detects all four failed rule categories in `multiple_violations`, the one-cent mismatch in `ambiguous`, and no violations in `valid_expense`.
- [ ] Exactly $100.00 for a meal and exactly $500.00 without approval pass their respective boundaries; one cent above fails.
- [ ] Invalid amounts and malformed reports fail closed.
- [ ] A blocked submission never executes the submission tool, and its violations reach the model as a tool result.
- [ ] An allowed submission executes the tool and reports zero failed rules.
- [ ] The run log shows every cycle and prompts for Return after each one. Cycle count depends on model tool calls and the final answer.
- [ ] Your threshold experiment and run notes cite what actually happened in the saved logs.

## Repository map

```text
exercise-hooks-starter/
├── examples/             # three supplied reports; add thresholds.json
├── hooks.py              # money parser, five checks, hook TODOs
├── agent.py              # working loop; hook integration and summary TODOs
├── models.py             # supplied HookResult
├── tools.py              # supplied retrieval and simulated submission tools
├── main.py               # supplied CLI and run summary
├── run_log.py            # supplied terminal-to-file logging
├── test_hooks.py         # supplied policy behavior checks
├── .env.example
├── requirements.txt
└── README.md
```
