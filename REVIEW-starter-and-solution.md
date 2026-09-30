# C2 Exercises: Starter and Solution Errors

This review lists **errors only**. For each module, it covers the starter (what learners get) and the solution (the reference answer). It is based on commit `c8048fe`.

**How it was checked**
- Every `.py` file compiled, every starter was diffed against its solution line by line, and every test suite was run.
- The code also ran with a scripted fake model, and live against Vocareum `gpt-4.1-mini` (about 260 calls).
- Every solution ran to completion live. The Hermes track wasn't run because the Hermes CLI isn't installed on the review machine; see the Hermes note at the end.

**Fix first**
1. Module 6: the Hermes starter TODOs don't state what the tests require.
2. Module 6: the solution's hard-coded Hermes path, and the permission-check bypass in its trace.
3. Module 4: the `agent.py` TODO leaves out `permission_check` and `authenticated_user`.
4. Module 3: three rules the tests check that no TODO states.

---

## Module 1 — Evaluator (C2.1)

**Starter** (there are no tests, so these cause wrong behaviour rather than failed tests)
- `README.md:47`, `:108`: the path given is `exercise-evaluator/`, but the folder is `exercise-evaluator-starter/`.
- `self_evaluation_loop.py:11-14` and `external_evaluation_loop.py:10-13`: the prompt TODOs don't state the `LABEL: PASS` line format the parsers depend on. Any other format silently fails closed.
- `external_evaluation_loop.py:66-71`: "return … raw feedback" is ambiguous. If a learner returns only the FEEDBACK line, a spurious false positive is reported on every cycle.
- `external_evaluation_loop.py:91-93`: the TODO doesn't say how the per-criterion Self column is filled in.

**Solution**
- `self_evaluation_loop.py:12-23`: the starter TODO says PASS must mean every criterion passed. The prompt never says so, and the code reads only the `VERDICT` line, so a review with a failed criterion but `VERDICT: PASS` is accepted.
- `self_evaluation_loop.py:27`: the comment says the verdict is read from the first output line, but the code scans every line.
- `.gitignore`: it lists only `output/`. `.env` and `__pycache__/` aren't ignored, and 17 `.pyc` files are tracked.

## Module 2 — Skills (C2.2)

**Starter**
- `agent.py:15-17`: the `SKILL_TOOL` TODO doesn't give the flat Responses API tool shape. The more familiar Chat Completions nesting causes a runtime API error.
- `agent.py:107-111`: the TODO doesn't mention setting `instructions` on cycle 2. `previous_response_id` doesn't carry them over, so the call that writes the campaign loses the no-invented-claims rules.
- `README.md:74-75`: two completion checks ("unknown skill name", "no skill selected") can't be triggered with the supplied briefs.

**Starter vs solution**
- `README.md:26`, `:77` (starter) vs `README.md:14` (solution): the final tasks differ. The starter asks learners to edit the magazine skill; the solution README uses the email skill. The starter's task has no worked answer.

## Module 3 — Hooks (C2.3)

**Starter** (these fail tests)
- `hooks.py:37-38`, `:46-47`: the TODOs don't say to skip amounts that fail to parse, so `test_invalid_money_values` raises a `TypeError`.
- `hooks.py:53-57`: "missing receipt ID" isn't defined, and the test treats an empty string as missing.
- `hooks.py:82`: the TODO doesn't say a rejected report must carry a violation message, which the test asserts.
- `agent.py:148-160`: "return a result" is wrong, because the code must set `result` and fall through. A literal `return` breaks the `(event, tool_output)` return value. The TODO also doesn't name `event["submission_executed"]`, which drives the final status.

**Solution**
- `agent.py:249-268`: there's no `count_failed_rules`. Starter TODO 6 asks for it, and the starter calls it at line 262, but the solution does the counting inline.
- `test_hooks.py` is missing from the solution folder.

## Module 4 — Permissions (C2.4)

**Starter** (these fail tests)
- `agent.py:110-124`: the TODO never names `event["permission_check"]` or its values `"ALLOWED"`/`"DENIED"`, and `INSTRUCTIONS.md:16,146,151` says `ALLOW`/`DENY`. A learner who follows either fails 3 tests.
- Same TODO: the denial record must use the key `authenticated_user`, but the TODO only says "authenticated identity". Any other key fails a 4th test.

**Starter and solution (shared tests)**
- `test_permissions.py`, `INSTRUCTIONS.md:271`, `:343-353`: the docs say the tests "check the complete role matrix", but a fail-open policy passes all 15 tests.

## Module 5 — Harness evaluation (C2.5)

**Starter**
- `metrics.py:474-483` and `INSTRUCTIONS.md:230`, `:255`: the TODOs don't say that result rows without study metadata must be handled without crashing; otherwise 2 tests fail with a `KeyError`. They also don't say invalid metadata must return `planned_trials=None`; returning `0` causes a `ZeroDivisionError`.
- `INSTRUCTIONS.md:46-48`: it says the failing tests are `NotImplementedError`s, but 5 more fail as assertion errors, including 4 supplied loop tests.
- `INSTRUCTIONS.md:495-497`: the checklist says passing tests prove the thresholds and metadata checks, but most of that logic can be skipped and still pass 28/28.
- `harness-evaluation.md:11`: asks for a run date that nothing records. `OPTIONAL` is never defined, and there's no slot for the judge overhead that `INSTRUCTIONS.md:485` requires.

**Solution**
- `metrics.py` around 716 and 796: the ablation report lists failure categories that happened in neither config being compared. `failure_runs` is a `defaultdict`, and reading it inserts empty keys. **Confirmed live**: the Permissions section listed categories that occurred only in the no-hooks run.
- There's no reference version of `harness-evaluation.md`, which `INSTRUCTIONS.md:33-41` lists as a learner deliverable.

## Module 6 — Production harness (I2.6)

**Starter**
- `hermes/configured_plugin.py:172`, `:209`: the block format `{"action": "block", "message": <JSON string>}` isn't stated anywhere, and there's no link to Hermes docs.
- `hermes/configured_plugin.py:230`: the TODO says "Block final verification", but the test requires `{"action": "continue"}`, and `"block"` fails.
- `hermes/configured_plugin.py:183`, `:220`: tool results arrive as JSON strings and must go through `_parsed_result`, which no TODO mentions. Passing the raw string raises an `AttributeError`.
- `hermes/configured_plugin.py:141`: `register_skill` must get the bare name `xyz-api-client`, and the qualified name fails the test. The TODO doesn't say which name goes where.
- `hermes/configured_plugin.py:250-261`: the Hermes learner must build the policy and hooks and work out the skill path. The README doesn't say so, and on the Python track this is done for the learner.
- `python/loop/configured_agent_loop.py:178`, `:209`, `:221`: the event names `permission_decision` and `hook`, and the values `"allow"`/`"deny"`, aren't stated. Only a paid live run catches a mistake.
- `README.md:580`: the completion check is "all six tests pass", but 5 of the 6 offline tests pass on the untouched starter.
- `README.md:706-716`: the expected output `HERMES COMPLETION CHECK — COMPLETED` is never printed in that form. Hermes prints `--- HERMES COMPLETION CHECK ---` and then `Status: COMPLETED`.
- `README.md:388-401`: there are no Hermes install instructions. This only matters for learners running locally.

**Solution**
- `hermes/run_exercise.py:32`: the author's machine path is hard-coded as `Path("/Users/peter/.local/bin/hermes")`, where the starter uses `Path.home()`. `test_installed_hermes_loads_plugin_offline` fails, and every solution Hermes command fails unless `HERMES_CLI` is set. `README.md:376` gives a third path.
- `hermes/runs/run.jsonl:17`: Hermes's `tool_call` meta-tool produced a tool result with no `permission_decision` before it (9 decisions, 10 results), so calls routed through `tool_call` skip the policy. This contradicts README Task 4 and `harness-comparison.md:48`.
- `harness-comparison.md`:
  - Lines 4 and 78 report "5 / 10 deterministic, live deselected", which contradicts the acceptance criteria of 6 and 11 passed, including the live probe.
  - Line 58 claims Hermes configuration work that is all supplied.
- `*/runs/*` and `README.md:226-236`, `249-251`, `926-927`: the committed runs contain the author's absolute paths, and the README lists `solution/...` paths that don't exist once you've changed into `solution/`.

**Module root**
- `opencode.json:20`, `:55`: fails the OpenCode schema check because of the `hooks` and `description` keys. The `hooks` block copies the Claude Code format with environment variables that don't exist, so it can never run. Nothing in module 6 references this file.
- `opencode.json:44-51`: the "read-only, offline" evaluator allows `bash` and `webfetch`.

---

## If Hermes is installed in the workspace

- **Starter:** every error above still holds, except the missing install instructions, which then only affect local learners. Four more unstated requirements also become reachable and will fail learners who follow the TODOs: the `skill_registered` event, a `permission_decision` event with `requested_capability`, the plugin's own `completion` event, and `tool_result` events carrying `arguments.url`.
- **Solution:** every error above still holds, and two get worse:
  - The hard-coded `/Users/peter` path becomes the blocker.
  - The `tool_call` permission bypass is no longer just a stale trace; it becomes a real path around the policy.
- The solution's Hermes track has not been run end to end. Once the path is fixed, it still needs a run with `HERMES_CLI` set.
