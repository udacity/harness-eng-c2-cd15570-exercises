# Production Harnesses: Python Loop versus Hermes

## Your assignment

Work through Tasks 1–7 in order. Your coding task is specifically to make the
supplied skill, hooks, and permission policy available at the correct lifecycle
boundaries in both harnesses.

The only implementation TODOs are in:

```text
python/loop/configured_agent_loop.py
hermes/configured_plugin.py
```

Do not rewrite the supplied components, API server, runners, baseline
harnesses, or tests. The incomplete `task/src/xyz_api_client.py` is also
intentional: you do not complete it by hand. In Task 5, each configured harness
must give an isolated copy to its own agent and let that agent implement the
client. You will then use the generated artifacts to compare the harnesses.


## Exercise at a glance

A complete local XYZ API server is supplied and ready to receive data. The missing piece is a Python client function that sends data to its synchronization endpoint. Before writing that function, the agent in each harness must call the API's documentation endpoint to learn the contract.

You are given:

- a working hand-built Python agent loop.
- a working Hermes production harness.
- a separate skill, hook set, and permission policy for each harness, with equivalent behavior.
- an incomplete API client.
- a complete XYZ API server that runs at `http://localhost:8080`.
- all integration and behavioral tests.

Your job is to connect the supplied production loop components to the handwritten Python loop and to the production Hermes loop. You then run each harness on a separate copy of the incomplete client. The agents, not you, implement the missing client function. You test both generated clients and compare how much work was required to configure each harness.

```text
                         WHAT YOU ARE GIVEN

        incomplete client + each harness's own components
                                  |
                         WHAT YOU CONNECT
                                  |
                  +---------------+---------------+
                  |                               |
                  v                               v
       Hand-built Python loop                  Hermes
                  |                               |
                  v                               v
       Agent completes its own          Agent completes its own
          client workspace                 client workspace
                  |                               |
                  +-----------+   +---------------+
                              |   |
                              v   v
                    Local XYZ API on port 8080
                 /health  /api-docs  /v2/data-sync
                              |   |
                  +-----------+   +---------------+
                  |                               |
                  v                               v
       Python-loop client result          Hermes client result
                  |                               |
                  +---------------+---------------+
                                  |
                       Matching supplied tests
                                  |
                                  v
               Compare correctness and integration effort
```

This directory is the exercise workspace. Complete the tasks in order and keep
the evidence produced by each task for the final comparison.

## Expected outcome

The expected result is:

- both harnesses complete the task;
- both generated clients pass the same behavioral tests;
- both harnesses enforce the same hooks and permission boundary; and
- the final comparison explains the observed integration effort and maintenance tradeoffs.

You must support that final comparison with test output and run evidence rather than assuming the outcome.

## Scenario

The fictional **2026 XYZ API** is a local JSON service running at:

```text
http://localhost:8080
```

The API is newer than the model's training data. The agent should therefore obtain the contract from the local documentation endpoint instead of guessing its authentication scheme, endpoint, headers, or request-body format.

The API contract is not included in the agent's task prompt. During each run, the agent must retrieve it from `GET /api-docs`.

### Available API endpoints

#### `GET /health`

This endpoint confirms that the local XYZ API server is available. It does not require authentication.

A successful request returns HTTP `200`:

```json
{
  "status": "ok",
  "version": "2026-03"
}
```

#### `GET /api-docs`

This endpoint returns the current machine-readable API contract. It does not require authentication. The response describes the API version, authentication format, token prefix, synchronization endpoint, required headers, request body, response fields, and common errors.

Because the XYZ API is fictional, its contract is not available on the public web. The agent must retrieve the contract from `GET /api-docs` before implementing the missing client function. During the configured task runs, both harnesses must block and log any attempt to access public web documentation. If a public web request is executed instead of denied, the harness is not configured correctly.

#### `POST /v2/data-sync`

This endpoint accepts the data that the completed client must synchronize.

The request must include these headers:

| Header | Required value |
| --- | --- |
| `Authorization` | `Bearer <token>`, where the token starts with `xyz-jwt-`. |
| `Content-Type` | `application/json`. |
| `X-API-Version` | `2026-03`. |
| `X-Client-ID` | A non-empty client identifier. |

The JSON request body must contain both fields:

```json
{
  "client": "your-client-id",
  "payload": {
    "data": "sample data"
  }
}
```

`client` must be a string identifying the caller. `payload` must be a JSON object containing the data to synchronize. The payload contents may be simple deterministic sample data; the tests focus on the required structure and protocol.

A valid request returns HTTP `200` with a response shaped like:

```json
{
  "status": "synced",
  "sync_id": "generated-uuid",
  "timestamp": "ISO-8601 timestamp",
  "received_client": "your-client-id",
  "payload_size": 25
}
```

The generated UUID, timestamp, and payload size vary by request. Tests should validate their type and meaning rather than compare them with fixed values.

The server returns deterministic error categories:

| Status | Cause |
| --- | --- |
| `400` | Missing client ID, wrong API version, invalid JSON, or missing `client`/`payload` fields. |
| `401` | Missing or malformed Bearer authentication, or a token without the `xyz-jwt-` prefix. |
| `404` | Any unsupported endpoint. |

All server responses use JSON. Errors contain an `error` field describing the rejected request.

### What must be implemented

A complete XYZ API server is supplied at `api_server/server.py` and runs locally at `http://localhost:8080`. This is one shared server used by both harnesses; there is no separate Python-loop server or Hermes server. The server already implements its health, documentation, and data-synchronization endpoints. You do not need to create an API server, add an endpoint, or change `api_server/server.py`.

The missing code is on the client side: Python code that sends data to the existing `POST /v2/data-sync` endpoint and returns the server's response.

That client-side behavior must be implemented in this function:

```python
def connect_to_xyz_api() -> dict:
    """Synchronize sample data with the local XYZ API and return its JSON result."""
```

Each harness receives an identical fresh copy of this incomplete function. During its run, the harness's agent must complete `connect_to_xyz_api()` so that calling it:

1. uses `http://localhost:8080` as the API base URL;
2. creates a small JSON payload containing sample data;
3. sends that data to `POST /v2/data-sync` using the API contract the agent learned from `/api-docs`;
4. includes the required Bearer token, version, client ID, and JSON content headers;
5. includes both required body fields, `client` and `payload`;
6. uses an explicit timeout for the synchronization request;
7. parses every JSON response;
8. returns the response body as a Python dictionary on both API success and API rejection; and
9. catches connection and timeout failures and returns a dictionary containing an `error` message instead of raising an uncaught exception.

Before implementing `connect_to_xyz_api()`, the agent must retrieve the contract from `GET http://localhost:8080/api-docs` and use it to construct the `/v2/data-sync` request; the run trace must record this documentation call.

The behavioral tests call this function and confirm that a successful result contains `status == "synced"`, a non-empty `sync_id`, a timestamp, and the expected client information. Separate API fixtures confirm that malformed authentication and requests produce the documented structured JSON errors.

You do not manually write the missing function during the measured runs. You connect the supplied controls to each loop and let each agent produce its own implementation.

## What you are given

All of the following are supplied in this starter directory:

| Supplied item | What it provides |
| --- | --- |
| Incomplete client template | The same missing `connect_to_xyz_api()` task for both agents. |
| Complete local XYZ API server | The running service, the documentation the agent must read, and the synchronization endpoint the generated client must call. |
| API server tests | Verify every supplied server endpoint before you configure either harness. |
| Hand-built Python loop | A functioning model-and-tool loop with integration points. |
| Hermes deployment | A functioning production harness for the same model task. |
| Python component set | The skill, hooks, and permission code used only by the hand-built Python loop. |
| Hermes component set | The equivalent skill, hooks, and permission configuration used only by Hermes. |
| Python tests and runner | Verify the Python integration, create its run workspace, and invoke the hand-built loop. |
| Hermes tests and runner | Verify the Hermes configuration, create its run workspace, and invoke Hermes. |

You are not asked to implement the loops, skill logic, hook logic, policy rules, local API server, or tests. That code is supplied.

## What you need to do

Your implementation work is limited to connecting the supplied components.

For the hand-built Python loop, you must:

- load the supplied skill into the agent context;
- call the permission policy before every tool execution;
- attach the syntax hook after client edits;
- attach the repeated-call hook before tool execution;
- attach the completion hook before accepting completion; and
- record skill, permission, hook, tool, and completion events.

For Hermes, you must:

- install or register the skill supplied under `hermes/components/`;
- apply the permission policy supplied under `hermes/components/`;
- register the hooks supplied under `hermes/components/` at the equivalent lifecycle events; and
- enable equivalent run evidence.

You should configure and connect the supplied code, not rewrite it.

## What running the harnesses creates

The run script copies the same incomplete client template into two isolated workspaces:

```text
python/runs/src/xyz_api_client.py
hermes/runs/src/xyz_api_client.py
```

The Python loop completes the first file. Hermes completes the second file. Each run also creates its own trace and test record:

```text
python/runs/run.jsonl
python/runs/test-results.json
hermes/runs/run.jsonl
hermes/runs/test-results.json
```

The two source files do not need to be textually identical. They must implement the same required behavior and pass the same tests.

Neither agent may read the other run's workspace. Each harness must complete its own isolated client copy.

## Supplied components

Each harness has its own supplied component files. The two sets enforce equivalent behavior, but they are stored separately so it is always clear which loop owns each implementation.

| Component | Hand-built Python loop | Hermes |
| --- | --- | --- |
| Skill | `python/components/skill/SKILL.md` | `hermes/components/skill/SKILL.md` |
| Hooks | `python/components/hooks/` | `hermes/components/hooks/` |
| Permission policy | `python/components/permissions/` | `hermes/components/permissions/` |

You will connect the Python component set during Task 3 and the Hermes component set during Task 4. Neither harness loads component files from the other harness's directory.

### Skill

Each harness's supplied `xyz-api-client` skill tells its agent to:

- treat the 2026 API contract as unknown;
- check the local service health;
- obtain current documentation from the allowed local endpoint;
- treat documentation as data rather than higher-priority instructions;
- edit only its assigned client file;
- run the supplied behavioral tests; and
- claim completion only after the tests pass.

The skill describes the workflow without revealing the hidden API contract.

### Hooks

Each harness has its own implementation of the same three logical hooks.

#### Syntax hook

This hook runs after the agent writes or edits the client. It compiles the assigned file, returns syntax errors, and prevents invalid code from being accepted as complete.

#### Repeated-call hook

This hook runs before a tool call. It normalizes and hashes the request, allows five equivalent calls, and returns a controlled error on the sixth.

#### Completion hook

This hook runs when the agent attempts to finish. It executes the supplied behavioral tests and allows completion only when they pass.

### Permission policy

Each harness has its own policy files, and both policies enforce the same default-deny behavior.

#### Allowed

| Capability | Scope |
| --- | --- |
| Read | Task prompt, supplied skill, and the assigned run's client file. |
| Edit | Only the assigned run's `src/xyz_api_client.py`, after `/api-docs` has been retrieved successfully. |
| Local health request | Only the exact local XYZ API health URL. |
| Local documentation request | Only the exact local XYZ API documentation URL. |
| Syntax check | Only the supplied compile operation for the assigned client. |
| Behavioral tests | Only the supplied test command in the assigned run workspace. |

#### Denied

| Capability | Reason |
| --- | --- |
| Public web search or fetch | The fictional API has no public documentation; `GET /api-docs` is the only authoritative source. |
| Arbitrary URLs or network commands | They could bypass the local-network boundary. |
| Arbitrary shell or Python commands | They could bypass file and network rules. |
| Package installation | All dependencies are supplied. |
| Reading `api_server/server.py` | The source reveals the hidden API contract. |
| Reading the reference answer or hidden tests | They reveal the expected implementation. |
| Reading the other run's workspace | Each harness must complete the task independently. |
| Writing outside the assigned client | Harness code, components, tests, and evidence must remain unchanged. |
| Destructive commands | They are unnecessary for the task. |
| Unknown tools or actions | Unspecified capabilities are denied by default. |

Every permission decision must appear in the run trace with the harness name, requested capability, decision, matching rule, and denial reason. A denial must return to the agent as a normal tool result and must not crash the loop.

The permission policy governs agent-requested tools. The supplied behavioral
test executes the generated client as normal Python code; it verifies the
expected localhost request but is not an operating-system network sandbox.

## Task 1: Start and verify the supplied API server

Complete this task before testing or configuring either harness. The API server is a finished dependency. The agents will not implement or modify any of its endpoints.

From the starter directory, start the server in one terminal:

```bash
cd module-6-prod-harness/exercise-prod-harness-starter
python3 api_server/server.py
```

Leave that process running. In a second terminal, run the supplied server tests:

```bash
cd module-6-prod-harness/exercise-prod-harness-starter
python3 api_server/tests/test_api_server.py
```

The tests make real requests to `http://localhost:8080` and verify:

- `GET /health` returns the expected server status and version;
- `GET /api-docs` returns the data-sync contract;
- `POST /v2/data-sync` accepts a valid authenticated request;
- `POST /v2/data-sync` returns the documented errors for invalid requests; and
- unsupported paths return `404`.

All these endpoints must already work. The harness agents do not develop `/v2/data-sync`; they develop the client-side `connect_to_xyz_api()` function that calls it. If this test suite fails, fix the server environment before continuing. Do not work around a server failure by changing either harness or the client task.

## Task 2: Confirm both supplied harnesses work

Complete this task before changing any integration code or configuration.

Change to the starter directory:

```bash
cd module-6-prod-harness/exercise-prod-harness-starter
```

Install the hand-built loop's dependencies and configure its model credentials:

```bash
python3 -m pip install -r python/requirements.txt
cp python/.env.example python/.env
```

Open `python/.env`, replace the placeholder API key, and select a model available through the configured OpenAI-compatible endpoint. Keep this file local; it is ignored by Git.

Verify that Hermes is installed and that its active profile has a working model
and provider:

```bash
hermes --version
hermes config get model --json
```

The Hermes runner defaults to `$HOME/.local/bin/hermes`. If Hermes is
installed elsewhere, point the runner to it before continuing:

```bash
export HERMES_CLI="$(command -v hermes)"
```

The baseline commands below make live provider calls. The provider receives
the task prompt, the incomplete client returned by `read_file`, and the local
`/health` and `/api-docs` tool results. Confirm that this is acceptable for the
configured provider before running them.

Run the baseline test for each harness:

```bash
python3 -m pytest python/tests/test_harness_baseline.py
python3 -m pytest hermes/tests/test_harness_baseline.py
```

Each baseline test file first checks its read-only adapter deterministically and then runs the sequence through a live model. Each harness must read the incomplete client, call `GET /health`, call `GET /api-docs`, and return a non-empty final response. A passing test confirms that model configuration, response continuation, real tool execution, tool-result delivery, and loop termination work across at least four model calls. The terminal displays each executed baseline tool request and result plus the final summary; no interactive pause is required.

### What the baseline test does

The baseline uses this read-only sequence. The table shows the earliest valid
progression; retries or additional model reasoning can add calls.

| Earliest model call | Operation | What it proves |
| --- | --- | --- |
| 1 | `read_file` reads the incomplete `task/src/xyz_api_client.py`. | The model can request a file tool and receive the file contents. |
| 2 | `http_get` requests `http://localhost:8080/health`. | The loop can execute a local HTTP tool and return its JSON result. |
| 3 | `http_get` requests `http://localhost:8080/api-docs`. | The model can continue from one tool result and retrieve the API contract on a later turn. |
| 4 or later | The model returns a non-empty final response; the prompt asks it to finish with `HARNESS_OK`. | The loop recognizes a final response and stops. |

This is only a connectivity and control-flow check. It does not edit the client. Its purpose is to establish that both harnesses can complete the same multi-cycle model-and-tool workflow before you continue.

Then run the same multi-cycle probe through each harness's command-line runner:

```bash
python3 python/run_exercise.py --smoke-test
python3 hermes/run_exercise.py --smoke-test
```

Both commands must return:

```text
HARNESS_OK
```

The pytest commands and runner commands each start a new live model run. Running
both therefore repeats the probe and makes additional provider calls. The
pytest commands validate the baseline contract; the runner commands create the
canonical smoke artifacts used in the final comparison.

Confirm that the baseline runner created:

```text
python/runs/smoke.json
hermes/runs/smoke.json
```

If either baseline fails, stop. Fix the environment, dependencies, credentials, model configuration, or Hermes installation before you connect the exercise components.

## Task 3: Connect the components to the Python loop

### This is a student coding task

In this task, **you must add Python code** to
`python/loop/configured_agent_loop.py`. Running the test is not the task by
itself: the test only verifies the connection code that you write. Your Task 3
implementation must complete the scaffolded skill, permission, and hook
connection classes, construct them inside `HandBuiltAgentLoop`, and call them
from the correct loop boundaries described below.

The skill instructions, permission rules, and hook behavior are already
implemented under `python/components/`. Do not rewrite those components. Your
code makes the supplied components available to the configured agent loop.

Task 2 remains available as the unchanged “before” implementation in
`python/loop/baseline_agent_loop.py`. Make the Task 3 changes only in
`python/loop/configured_agent_loop.py`. Do not modify the supplied component
logic under `python/components/`, and do not change
`python/loop/baseline_agent_loop.py`.

The runner already constructs the supplied skill, permission policy, hooks, and
trace and passes them to `HandBuiltAgentLoop`. Complete every TODO in
`configured_agent_loop.py` so those objects become available at the correct
loop boundaries. Do not add TODOs or implementation changes to the supplied
component files.

### Complete three component-connection classes

Organize the integration around three explicit classes in
`configured_agent_loop.py`:

1. `SkillConnection`
   - Give the skill a name, description, and source.
   - Accept the supplied `SKILL.md` text and run trace.
   - Provide `add_to_context()`, which appends the skill instructions to the
     base model instructions and records a `skill_loaded` event.
2. `PermissionConnection`
   - Accept the supplied `PermissionPolicy` and run trace.
   - Provide `before_tool()`, which calls `policy.decide()` and records the
     resulting allow or deny decision before execution.
   - Provide `after_tool()`, which calls `policy.observe_result()` so successful
     documentation retrieval can advance trusted policy state.
3. `HookConnections`
   - Accept the supplied repeated-call, syntax, and completion hooks, plus the
     assigned client path and run trace.
   - Describe what each hook does.
   - Provide `before_tool()` for the repeated-call hook, `after_write()` for the
     syntax hook, and `before_completion()` for the completion hook.
   - Record every hook result in the structured trace.

### Connect the classes to the loop

In `HandBuiltAgentLoop.__init__()`, expose the three component types on the
configured loop:

```python
self.skill = SkillConnection(...)
self.permissions = PermissionConnection(...)
self.hooks = HookConnections(...)
```

Then connect them at these lifecycle boundaries:

```python
# Before the first model call
instructions = self.skill.add_to_context(base_instructions)

# Before every requested tool operation
decision = self.permissions.before_tool(tool, arguments, trace_arguments)

# After permission allows the request, but before execution
repeated = self.hooks.before_tool(tool, arguments)

# After tool execution
self.permissions.after_tool(tool, arguments, result)
result = self.hooks.after_write(tool, result)

# Before accepting the model's final response
completion = self.hooks.before_completion(...)
```

The required tool pipeline is:

```text
permission decision
        -> repeated-call hook
        -> tool execution
        -> policy result observation
        -> post-write syntax hook
        -> structured tool-result event
```

A denied permission decision or blocked repeated-call hook must return a
controlled tool result to the model without executing the requested operation.
The completion hook must also be used by the fixed `run_tests` tool and before
the loop accepts a final model response.

### Test only the component connections

Keep the XYZ API server from Task 1 running. From the starter directory, run:

```bash
python3 -m pytest -s python/tests/test_integration.py
```

This command includes one live-model component probe and five local edge-case
tests. The live probe must show the policy and hooks around this sequence:

1. request `GET /health`;
2. request `GET /api-docs`;
3. read the temporary incomplete client;
4. write the exact same source back to trigger the syntax hook;
5. run the probe test; and
6. pass the completion hook.

The probe uses a temporary workspace and must leave `NotImplementedError` in
the client. It does not implement `connect_to_xyz_api()`, modify `python/runs/`,
or create Task 5 evidence. The test sends its prompt, supplied skill, tool
requests and results, and temporary client context to the provider configured
by `OPENAI_BASE_URL`.

Task 3 is complete when all six tests pass and the probe client remains
incomplete. Do not run `python3 python/run_exercise.py --fresh` yet; that command
implements the client and belongs to Task 5.

## Task 4: Connect the components to Hermes

### This is a student coding task

In this task, **you must add Python code** to
`hermes/configured_plugin.py`. Running the test is not the task by itself: the
test verifies the connection code that you write. Your Task 4 implementation
must complete the scaffolded skill, permission, and hook connection classes,
construct them inside `HermesConfiguredPlugin`, and register them at the
native Hermes lifecycle boundaries described below.

Hermes owns its model/tool loop internally, so there is no Hermes loop file to
copy. The configured plugin is the integration layer that makes the supplied
components available inside that loop. It is the Hermes equivalent of
`python/loop/configured_agent_loop.py`.

Task 2 remains available as the unchanged “before” implementation in
`hermes/baseline_plugin.py`. Complete every TODO only in
`hermes/configured_plugin.py`. Do not modify the supplied component logic under
`hermes/components/`, and do not change `hermes/baseline_plugin.py`. The native
plugin entry point, manifest, runtime configuration, tool implementations, and
runner are supplied. They already select the baseline adapter for
`--smoke-test` and the configured adapter for configured runs.

### Complete three component-connection classes

Organize the integration around three explicit classes in
`configured_plugin.py`:

1. `SkillConnection`
   - Give the skill a name, qualified name, description, and source.
   - Accept the supplied `SKILL.md` path and run trace.
   - Provide `register()`, which calls `ctx.register_skill()` and registers a
     `pre_llm_call` hook that records the skill preload.
2. `PermissionConnection`
   - Accept the supplied `PermissionPolicy` and run trace.
   - Provide `before_tool()`, which calls `policy.decide()`, records the allow
     or deny decision, and blocks denied requests before execution.
   - Provide `after_tool()`, which calls `policy.observe_result()` and records
     the structured tool result.
3. `HookConnections`
   - Accept the supplied repeated-call, syntax, and completion hooks, plus the
     assigned client path and run trace.
   - Describe what each hook does.
   - Provide `before_tool()` for repeated calls, `after_write()` for syntax,
     and `before_completion()` for completion.
   - Record every hook result in the structured trace.

### Connect the classes to Hermes

In `HermesConfiguredPlugin.__init__()`, expose the three component types:

```python
self.skill = SkillConnection(...)
self.permissions = PermissionConnection(...)
self.hooks = HookConnections(...)
```

In `HermesConfiguredPlugin.register()`, attach them to native Hermes events:

```python
self.skill.register(ctx)
ctx.register_hook("pre_tool_call", self.before_tool)
ctx.register_hook("post_tool_call", self.after_tool)
ctx.register_hook("transform_tool_result", self.hooks.after_write)
ctx.register_hook("pre_verify", self.hooks.before_completion)
```

The `pre_tool_call` adapter must run the permission decision first. Only an
allowed request may reach the repeated-call hook and the tool implementation.
The `post_tool_call` adapter must let the policy observe trusted results. The
tool-result transformation must run the syntax hook after a successful client
write, and `pre_verify` must run the completion hook before Hermes accepts its
final response.

Register only these five task-scoped tools:

```text
read_file
write_file
http_get
web_search
run_tests
```

Hermes may independently request runtime discovery helpers such as
`tool_search` or `tool_describe`. Do not add them to the exercise toolset or
allowlist. The default-deny permission policy must block those requests and
return the denial to the model, which can then call the five registered tools
directly. A blocked request may still produce a Hermes tool-result lifecycle
event; that event is the denial being returned to the model, not the denied
capability being executed.

### Test only the component connections

Keep the XYZ API server from Task 1 running. From the starter directory, run:

```bash
python3 -m pytest -vv -s hermes/tests/test_integration.py
```

This command includes one live-model Hermes component probe plus local
connection and edge-case tests. The live probe must load the supplied skill and
print each skill, permission, hook, and tool-result event while Hermes is
running. While it waits for the next model response, it prints an elapsed-time
status every ten seconds. A waiting message is not a failure; the test fails
only if Hermes reports an error, the provider exceeds the timeout, an assertion
fails, or pytest reports a failed test.

The live probe must show the policy and hooks around this sequence:

1. request `GET /health`;
2. request `GET /api-docs`;
3. read the temporary incomplete client;
4. write the exact same source back to trigger the syntax hook;
5. run the probe test; and
6. pass the completion hook.

### Read the live probe evidence

A correctly connected run shows all of the following:

- `SKILL REGISTERED` followed by `SKILL LOADED INTO MODEL CONTEXT`;
- an `ALLOW` or `DENY` permission decision before every requested operation;
- `HOOK: repeated_call` after each allowed permission decision and before the
  corresponding exercise tool executes;
- successful results for both local HTTP requests and the assigned-file read;
- an allowed assigned-file write only after `/api-docs` succeeds;
- `HOOK: syntax_check` immediately after that write;
- an allowed `run_tests` request followed by a passing `completion_test` hook;
- a second passing `completion_test` when Hermes performs its final
  `pre_verify` check; and
- `HERMES COMPLETION CHECK — COMPLETED` before the final model response.

The two completion-hook results are intentional. The first belongs to the
explicit `run_tests` tool call. The second is the independent guard that runs
before Hermes accepts the model's final response.

The probe uses a temporary Hermes profile and workspace. It must leave
`NotImplementedError` in the temporary client, and it must not modify
`hermes/runs/` or produce Task 5 evidence. The test sends its prompt, preloaded
skill, tool requests and results, and temporary client context to the provider
configured in the active Hermes profile.

Task 4 is complete when pytest reports `11 passed`, the probe summary reports a
zero Hermes return code, and the temporary client still contains
`NotImplementedError`. Do not run
`python3 hermes/run_exercise.py --fresh` yet; that command implements the client
and belongs to Task 5.

## Task 5: Run both harnesses

Tasks 3 and 4 connected the components without implementing the client. Task 5
is the first time the configured harnesses receive the full XYZ API client
task. Each harness must independently discover the local contract and replace
`NotImplementedError` in its own generated client.

### Keep the local API server running

The two harnesses use the same supplied local server. If it is not already
running, start it in a separate terminal and leave that terminal open:

```bash
cd module-6-prod-harness/exercise-prod-harness-starter
python3 api_server/server.py
```

From the terminal where you will run the harnesses, confirm the server is
healthy:

```bash
cd module-6-prod-harness/exercise-prod-harness-starter
curl http://localhost:8080/health
```

The response must report `"status": "ok"`. Do not continue if this request
fails.

### Run the hand-built Python harness

From the starter directory, run:

```bash
python3 python/run_exercise.py --fresh
```

The `--fresh` option resets only the Python harness workspace by copying the
incomplete template from:

```text
task/src/xyz_api_client.py
```

The configured Python loop then asks a real model to complete
`connect_to_xyz_api()` and writes the generated implementation to:

```text
python/runs/src/xyz_api_client.py
```

The run also writes its structured evidence to:

```text
python/runs/run.jsonl
python/runs/test-results.json
```

Wait for this command to finish before starting Hermes.

### Run the configured Hermes harness

From the same starter directory, run:

```bash
python3 hermes/run_exercise.py --fresh
```

This `--fresh` option resets only the Hermes workspace from the same incomplete
template. Hermes then asks a separate real-model run to complete the function
and writes its generated implementation to:

```text
hermes/runs/src/xyz_api_client.py
```

The Hermes run writes its evidence to:

```text
hermes/runs/run.jsonl
hermes/runs/test-results.json
```

The runner prints the selected model, skill registration, every permission and
hook decision, and each tool result while Hermes works. If the provider has not
returned the next model response, the runner prints an elapsed-time message
every ten seconds. This means the process is waiting, not frozen.

The default `--timeout 300` is one wall-clock limit for the complete Hermes
run, not a separate 300-second allowance for every model call. Every new
`HERMES TOOL REQUEST` proves that another model call completed and that the loop
advanced. The run is not complete, however, until the model writes the client,
runs the tests, passes final verification, and returns its final response. If
the selected provider consistently needs more than five minutes for all loop
cycles, start a new run with a larger total limit:

```bash
python3 hermes/run_exercise.py --fresh --timeout 600
```

Pressing `Ctrl-C` cancels the active Hermes subprocess and exits without a
Python traceback. An interrupted run is incomplete and must not be used as
Task 5 evidence; rerun the same `--fresh` command to reset the Hermes workspace
and start again.

Hermes may call `run_tests` before it has implemented the client. A failed
`completion_test` at that point demonstrates that the completion hook blocked
premature completion. It is not the final run result if the model continues,
writes the client, and later produces a passing `run_tests` result. Likewise,
denied attempts to read files outside the assigned client demonstrate that the
permission boundary is working.

Run the two harness commands sequentially rather than concurrently. This keeps
their live output and provider usage easy to distinguish and makes failures
easier to diagnose.

### What each fresh run must do

Each harness must independently:

1. copy the incomplete client template into its own run directory;
2. invoke its configured loop with the XYZ API client task;
3. use the supplied skill to check the local service and discover its current
   API documentation;
4. use the permission policy and hooks around every requested operation;
5. write the API call inside `connect_to_xyz_api()` in its assigned run copy;
6. run the supplied behavioral test and pass the completion hook; and
7. save the generated client, structured trace, and test result.

These commands make real model-provider calls and may take several minutes.
Their prompts, skill instructions, tool requests and results, and assigned
client contents are sent to the configured providers.

Do not edit either generated client by hand, and do not copy a completed
client from one run into the other. The purpose of Task 5 is to observe each
harness completing the same task independently.

### Confirm both runs completed

After both commands finish, confirm that these two files exist and no longer
contain `NotImplementedError`:

```text
python/runs/src/xyz_api_client.py
hermes/runs/src/xyz_api_client.py
```

For Hermes, a successful terminal summary must contain:

```text
"status": "completed"
"returncode": 0
"tests_passed": true
```

Before that summary, the live output must show a successful `write_file`, a
passing `syntax_check`, a passing `run_tests` result, and
`HERMES COMPLETION CHECK — COMPLETED`. The two generated implementations do not need to be textually identical;
each one must satisfy the same behavioral contract.

The Python runner must likewise report `"status": "completed"` after its
completion hook passes. If a run fails or times out, inspect that harness's
terminal output and `run.jsonl` before rerunning its `--fresh` command.
Rerunning `--fresh` discards that harness's previous generated client and run
evidence and starts again from the incomplete template. After a successful
run, do not invoke `--fresh` for that harness again unless you intentionally
want to replace its successful client and evidence.

## Task 6: Test the results

Run each harness's complete supplied test suite from the starter directory:

```bash
python3 -m pytest python/tests
python3 -m pytest hermes/tests
```

These complete suites include the live baseline tests, so they make additional
model-provider calls. Keep the XYZ API server running while both suites run.

The tests verify:

- both baseline harnesses work;
- the supplied skill is active in both configured harnesses;
- the hooks run at the correct lifecycle events;
- both permission implementations allow and deny the same operations;
- permission denials return to the agent without crashing;
- the two completed client files exist;
- both clients call the local XYZ API correctly; and
- both clients return the expected successful result.

Both harnesses should produce similar test results: the full suite should pass for both generated clients. Similar results mean equivalent observable behavior, not identical source code or identical model traces.

During each fresh configured run, the completion hook saves its latest
behavioral-test result under the corresponding harness directory:

```text
python/runs/test-results.json
hermes/runs/test-results.json
```

## Task 7: Compare the harnesses

After both harnesses and both test suites pass, create:

```text
harness-comparison.md
```

This file is your final written exercise deliverable. It is not supplied in advance and is not created by either agent. You write it after reviewing the two generated clients, test results, run traces, and integration code.

Store the file at the root of the starter directory because it compares both harnesses. Harness-specific evidence remains in:

```text
python/runs/
hermes/runs/
```

Use these artifacts as evidence:

- `python/runs/src/xyz_api_client.py` and `hermes/runs/src/xyz_api_client.py`;
- both `run.jsonl` traces;
- both `test-results.json` files;
- the Python integration code; and
- the Hermes configuration and adapter code.

Begin `harness-comparison.md` with this outcome table:

| Evidence | Hand-built Python loop | Hermes |
| --- | --- | --- |
| Baseline smoke test | Pass or fail | Pass or fail |
| Integration tests | Pass or fail | Pass or fail |
| Skill loaded | Trace evidence | Trace evidence |
| Hook tests | Pass or fail | Pass or fail |
| Permission tests | Pass or fail | Pass or fail |
| Generated client | Artifact path | Artifact path |
| Client behavioral tests | Pass or fail | Pass or fail |
| Task completed | Yes or no | Yes or no |

Then explain:

1. how you loaded the skill in each harness;
2. how you attached each hook;
3. how you enforced the permission policy;
4. how much Python integration code the hand-built loop required;
5. how much Hermes configuration or adapter code was required;
6. which harness returned clearer errors and traces; and
7. which approach would be easier to maintain.

Base the architectural conclusion on the captured evidence. Consider which
boundaries each harness owns, how much custom dispatch and state are required,
how lifecycle events and permissions are connected, and which implementation
would be easier to maintain.

Do not support that conclusion with line count alone. Use the passing results plus the number of integration points, custom state, configuration steps, and application-owned boundaries.

## Final exercise acceptance criteria

The exercise is complete when:

- [ ] all work and generated artifacts are under `module-6-prod-harness/exercise-prod-harness-starter/`;
- [ ] the complete supplied API server passes `python3 api_server/tests/test_api_server.py` before either harness is configured;
- [ ] both untouched harnesses pass the baseline checks;
- [ ] the components under `python/components/` are connected to the Python loop;
- [ ] the components under `hermes/components/` are connected to Hermes;
- [ ] both integration test files pass;
- [ ] both harnesses start from isolated copies of the same incomplete client;
- [ ] both harnesses produce a completed `connect_to_xyz_api()` implementation;
- [ ] both generated clients pass the same behavioral tests;
- [ ] both traces demonstrate the required hooks and permission decisions;
- [ ] the comparison report uses captured evidence; and
- [ ] the comparison explains the observed difference in integration work.

## Starter directory layout

Keep all of your work and generated evidence in this starter directory:

```text
module-6-prod-harness/
└── exercise-prod-harness-starter/
    ├── README.md
    ├── task/
    │   └── src/
    │       └── xyz_api_client.py          # incomplete template
    ├── python/
    │   ├── loop/
    │   │   ├── baseline_agent_loop.py       # unchanged Task 2 loop
    │   │   └── configured_agent_loop.py     # Task 3 loop with components
    │   ├── components/
    │   │   ├── skill/
    │   │   │   └── SKILL.md
    │   │   ├── hooks/
    │   │   │   └── hooks.py
    │   │   └── permissions/
    │   │       └── policy.py
    │   ├── tests/
    │   │   ├── test_harness_baseline.py
    │   │   ├── test_integration.py
    │   │   └── test_generated_client.py
    │   ├── requirements.txt
    │   ├── .env.example
    │   ├── run_exercise.py                 # Python-loop runner
    │   └── runs/
    │       ├── src/
    │       │   └── xyz_api_client.py       # generated Python-loop client
    │       ├── smoke.json
    │       ├── run.jsonl
    │       └── test-results.json
    ├── hermes/
    │   ├── .hermes/
    │   │   ├── config.yaml                 # Hermes deployment configuration
    │   │   └── plugins/
    │   │       └── xyz-api-harness/         # native exercise plugin entry point
    │   ├── baseline_plugin.py               # read-only Task 2 baseline tools
    │   ├── configured_plugin.py             # Task 4 adapter with components
    │   ├── components/
    │   │   ├── skill/
    │   │   │   └── SKILL.md
    │   │   ├── hooks/
    │   │   │   └── hooks.py
    │   │   └── permissions/
    │   │       └── policy.py
    │   ├── tests/                          # supplied Hermes tests
    │   ├── run_exercise.py                 # Hermes runner
    │   └── runs/
    │       ├── src/
    │       │   └── xyz_api_client.py       # generated Hermes client
    │       ├── smoke.json
    │       ├── smoke.jsonl
    │       ├── run.jsonl
    │       └── test-results.json
    ├── api_server/                         # one complete server shared by both harnesses
    │   ├── server.py
    │   └── tests/
    │       └── test_api_server.py          # verifies every supplied endpoint
    └── harness-comparison.md               # your final cross-harness report
```
