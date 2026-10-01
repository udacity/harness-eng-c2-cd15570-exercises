# Module 3 Demo: Deterministic Hooks for Incident Mutations

This demo continues the same `INC-2048` incident-response use case from Modules
1 and 2. Production `checkout-api` is `DEGRADED` with an 18% error rate while
`checkout-v42` is deployed. `checkout-v41` is the last-known-good version;
rollback, recovery, and resolution are initially unconfirmed.

Module 1's independent final-note evaluation and Module 2's on-demand skills
are supplied here. Module 3 adds production tools and a deterministic
`before_tool_call` hook:

| Mode | Mutation path | What it demonstrates |
| --- | --- | --- |
| `basic` | Model proposes mutation → tool executes | Instructions and skills can advise the model, but no code enforces their advice. |
| `hooks` | Model proposes mutation → hook checks trusted state → tool executes or is blocked | Deterministic invariants control the execution boundary. |

Both modes use the same prompt, skills, scenario, tool definitions, and agent
loop. Only the hook setting changes. The simulated tools have no hidden safety
policy, so the comparison remains visible.

## The execution boundary

The agent first loads relevant skills and gathers current incident, health,
deployment, and log evidence. The prompt then requires it to request every
mutation named by the operator, even when the model believes one is unsafe. A
tool request is only a proposal; the harness owns the decision.

```text
model proposes rollback_deployment or update_incident_status
                              |
                              v
                    harness receives call
                       /             \
                  basic              hooks
                    |                  |
                    |          before_tool_call
                    |          runs Python checks
                    |             /        \
                    |          ALLOW       BLOCK
                    |            |           |
                    v            v           v
              execute tool   execute tool   return violations
                    \            /           /
                     \__________/___________/
                              |
                              v
               model receives function result
                              |
                              v
                  grounded 60-word final note
```

When a hook blocks a call, the mutation tool does not run. The violations are
returned through `function_call_output`, and the loop continues so the agent
can explain the result. The hook does not write the final response or choose
the number of model cycles.

## Deterministic invariants

Every well-formed mutation is evaluated against all five checks:

1. A service-health snapshot was retrieved during the current run. Successful
   mutation invalidates that evidence, so a later mutation needs a new check.
2. A requested rollback target exists in trusted deployment history.
3. A requested rollback target is marked last-known-good.
4. The exact same mutation has not already executed in the run.
5. `RESOLVED` is allowed only when service health is `HEALTHY` and recovery is
   confirmed.

Unknown hook targets, malformed arguments, invalid statuses, and incident-ID
mismatches fail closed. `HookResult` contains one combined `allowed` decision,
the pass/fail result of every applicable check, and every violation. The checks
use ordinary Python and make no model calls.

These invariants are intentionally narrow. The authenticated user is shown but
their `support_engineer` role is not authorized or rejected here; permission
enforcement is the new responsibility introduced in Module 4.

## Scenarios

| Scenario | Requested mutation | Expected basic result | Expected hooks result |
| --- | --- | --- | --- |
| `unsafe_remediation` | Roll back to known but not last-known-good `checkout-v40`, then mark `RESOLVED` while degraded | Both execute; state becomes inconsistent | Both blocked; original state remains |
| `valid_rollback` | Roll back once to last-known-good `checkout-v41` | Executes | All checks pass and it executes |
| `premature_resolution` | Mark the degraded, unrecovered incident `RESOLVED` | Executes | Resolution check blocks it |

The scenario files are ordinary inputs. They include the same authenticated
user now so Module 4 can build on the contract without changing the use case.

## Run the reliable classroom demo

The default scripted provider requires no API key or dependency installation:

```bash
cd module-3-hooks/demo
python3 main.py compare
```

The default `unsafe_remediation` run makes the contrast explicit. Basic mode
finishes at `checkout-v40` and `RESOLVED`; hooks mode remains at `checkout-v42`
and `INVESTIGATING`. Then show the allow path and the single-rule block:

```bash
python3 main.py hooks --scenario valid_rollback
python3 main.py compare --scenario premature_resolution
```

Run one mode by itself with `python3 main.py basic` or `python3 main.py hooks`.
Add `--pause` to wait for Return after every model cycle. Each run writes a
timestamped transcript under `output/`.

The scripted fixture provides stable tool choices and exact 60-word responses.
Its token counts are illustrative request-size estimates, and its near-zero
timings are not real model latency.

## Run with a live model

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Add the course API key to `.env`, then run:

```bash
python3 main.py compare --provider live
python3 main.py hooks --scenario valid_rollback --provider live
```

Use `--model` to override `OPENAI_MODEL`. The default endpoint is
`https://openai.vocareum.com/v1`; `OPENAI_BASE_URL` can override it. `.env` and
generated logs are ignored by Git.

A live model can choose a different number or order of retrieval and skill
calls. It may also omit a requested mutation despite the prompt. The summary
reports what actually happened; the harness never manufactures a tool call.

## What is inherited from earlier modules

Module 2's four complete skills remain in `skills/`. The prompt receives only
their names and descriptions. `load_skill` validates an exact catalog name and
returns the complete selected file, preserving progressive disclosure inside a
longer tool loop.

After the agent finishes, `evaluator.py` preserves Module 1's boundary:

- Python verifies exactly 60 whitespace-separated words and `INC-2048`.
- A fresh model conversation judges factual grounding and the usefulness of
  the next step against final state and execution evidence.

Evaluator tokens and time are printed as benchmark overhead and excluded from
serving metrics. This keeps evaluation separate from the execution policy: a
post-response evaluator can detect a bad outcome, but only the before-tool hook
can prevent it.

## What to show during the demo

1. Open `tools.py` and show that mutation functions update state without policy
   checks.
2. Open `hooks.py` and connect each named check to one exact invariant.
3. Run the unsafe scenario in `basic`; point out that safe-remediation guidance
   was loaded, yet both unsafe calls still executed.
4. Run the same scenario in `hooks`; follow the health retrieval, proposed
   call, check results, blocked result, and unchanged state.
5. Confirm that the blocked result returns to the model rather than ending the
   process at the hook.
6. Run `valid_rollback` to prove the hook is a gate, not a blanket prohibition.
7. End on the state comparison and the separate independent evaluation.

## From this demo to the exercise

The exercise uses expense submission rather than incident remediation, but the
student work has the same structure:

| Demo implementation | Exercise task |
| --- | --- |
| Five functions in `hooks.py` | Implement the five exact expense-policy checks |
| `validate_mutation()` | Run every check and combine all findings in one `HookResult` |
| `before_tool_call()` | Fail closed and validate immediately before the sensitive tool |
| The `mode == "hooks"` branch in `_tool_result()` | Connect the hook to the agent/tool loop |
| Blocked `function_call_output` | Return violations to the model without executing submission |
| `count_failed_rules()` and `print_summary()` | Report hook execution, violations, and actual tool execution accurately |
| Direct permissive mutation tools | Keep business policy out of the underlying tool implementation |

In the exercise, the sensitive action is `submit_expense_report`; here it is a
production rollback or status update. In both cases, the model chooses when to
request a tool, the harness resolves trusted state, and deterministic code must
decide before the side effect happens.

## Deterministic tests

```bash
python3 -m unittest discover -s . -p 'test_*.py'
```

The tests require no API key. They cover every allow/block invariant,
fail-closed inputs, permissive underlying tools, catalog-only skill routing,
unsafe basic execution, blocked tool feedback, a valid allow path, exact
60-word output, and the fresh independent evaluation boundary.

## Repository map

```text
demo/
├── main.py                    # CLI, paired runs, summaries, and logging
├── agent.py                   # shared model/tool loop and optional hook boundary
├── hooks.py                   # five deterministic mutation invariants
├── tools.py                   # simulated retrieval and permissive mutation tools
├── models.py                  # HookResult structure
├── catalog.py                 # skill discovery and exact on-demand loading
├── clients.py                 # deterministic Responses API fixture
├── evaluator.py               # supplied Module 1 evaluation boundary
├── scenario.py                # trusted scenario loading and context
├── run_log.py                 # timestamped terminal logs
├── scenarios/                 # unsafe, valid, and premature mutation requests
├── skills/                    # supplied Module 2 incident-response skills
├── test_demo.py
├── .env.example
└── requirements.txt
```

Module 4 can retain this entire flow and add deterministic role and resource
authorization before an allowed mutation reaches its tool.
