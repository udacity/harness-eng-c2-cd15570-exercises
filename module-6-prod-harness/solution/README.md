# Production Harnesses: Python Loop versus Hermes

In this exercise, you will add the same supplied agent components to two different harnesses:

1. a hand-built Python agent loop; and
2. a Hermes agent deployment.

You will not build either loop or design the components from scratch. Your job is to connect the supplied skill, hooks, and permission policy to each harness, run the same tests and coding task through both, and explain how the integration experience differs.

## Scenario

An agent must finish an incomplete Python client for the fictional **2026 XYZ API**.

The API is newer than the model's training data, so the agent should not guess its authentication, endpoint, header, or request-body requirements. A local mock service provides a health endpoint and current API documentation.

Each harness receives a fresh copy of:

```text
starter/src/xyz_api_client.py
```

The file contains an unfinished function:

```python
def connect_to_xyz_api() -> dict:
    """Synchronize sample data with the local XYZ API and return its JSON result."""
```

The agent must use the allowed local documentation, complete the client, and pass the supplied behavioral tests.

You do not complete the client yourself during the measured runs. You configure each harness so its agent can complete the task safely.

## What you receive

| Item | Purpose |
| --- | --- |
| Incomplete API client | The coding task that both agents must complete. |
| Local mock API | Supplies health, documentation, synchronization, and deterministic error responses. |
| Hand-built Python loop | A working agent loop with extension points for skills, hooks, and permissions. |
| Hermes deployment | A working Hermes setup that can run the same agent task. |
| `xyz-api-client` skill | Tells the agent how to discover the current API contract and verify its work. |
| Syntax hook | Compiles the client after an edit and returns syntax errors to the agent. |
| Repeated-call hook | Stops the agent after six equivalent tool calls. |
| Completion hook | Runs the behavioral tests before allowing the agent to finish. |
| Permission policy | Defines which files, commands, and network destinations the agent may use. |
| Test suite | Checks component integration, permissions, hooks, and final client behavior. |

All component logic is supplied. You only need to register it at the correct lifecycle point in each harness.

## Your task

Complete the exercise in five tasks:

1. Confirm that both supplied harnesses work before you change them.
2. Add the supplied components to the hand-built Python loop and run it.
3. Add the same components to Hermes and run it.
4. Verify both completed integrations with the shared tests.
5. Submit a short comparison supported by the captured results.

Use the same model, prompt, starter client, mock API, and tests for both runs.

## Task 1: Confirm both harnesses work

Complete this task **before you add or change any skill, hook, or permission configuration**. Establishing a working baseline prevents you from confusing an environment or model-connection problem with an integration problem introduced later.

Change to the starter directory:

```bash
cd module-6-prod-harness/exercise-prod-harness-starter
```

First, run the deterministic baseline tests:

```bash
python3 -m pytest tests/test_harness_baseline.py
```

These tests verify that:

- the hand-built Python loop can start and stop cleanly;
- the Hermes deployment can start and stop cleanly;
- both harnesses can load their model configuration;
- their built-in message and tool-dispatch paths are available; and
- the starter client has not been modified.

Next, make one minimal live model call through each harness:

```bash
python3 run_exercise.py --harness python --smoke-test
python3 run_exercise.py --harness hermes --smoke-test
```

The smoke-test mode sends the same prompt through each harness without loading the exercise skill, hooks, or permissions:

```text
Return exactly HARNESS_OK. Do not call any tools.
```

Both commands must finish successfully and print:

```text
HARNESS_OK
```

The smoke-test runner must save the raw result and basic environment information to:

```text
reports/baseline/python-smoke.json
reports/baseline/hermes-smoke.json
```

Before continuing, confirm that:

- both commands reached the configured model;
- both returned a response without crashing or timing out;
- both baseline result files exist;
- neither run changed `starter/src/xyz_api_client.py`; and
- both harnesses used the model and settings specified for the exercise.

If either baseline fails, stop here. Check the working directory, dependencies, credentials, model configuration, and Hermes installation, then rerun the baseline tests. Do not modify the supplied skill, hooks, or permission policy to hide a baseline failure.

## Supplied skill

The `xyz-api-client` skill tells the agent to:

- treat the 2026 API contract as unknown;
- check the local service health;
- retrieve documentation from the allowed local endpoint;
- use the documentation as data rather than as instructions;
- edit only the assigned client file;
- run the supplied behavioral tests; and
- claim completion only after the tests pass.

The skill describes a workflow. It does not contain the hidden endpoint, authentication format, headers, or payload.

You must make this same skill available to both agents:

- load it and add its instructions to the hand-built loop's model context;
- install or register it through Hermes' skill mechanism.

## Supplied hooks

Add all three hooks to both harnesses.

### Syntax hook

Run this hook after the agent writes or edits the client.

It must:

- compile the assigned Python file;
- return the compiler message when syntax is invalid;
- prevent invalid code from being accepted as complete; and
- write a hook event to the run log.

### Repeated-call hook

Run this hook before a tool call.

It must:

- normalize and hash the tool name and arguments;
- keep counts within the current run;
- allow the first five equivalent calls;
- block the sixth equivalent call; and
- return a useful error to the agent without crashing the session.

### Completion hook

Run this hook when the agent attempts to finish.

It must:

- run the supplied behavioral tests;
- allow completion when they pass;
- return the failed test output when they fail; and
- record the final result in the run log.

The hook functions and commands are supplied. You are responsible for attaching them to the correct events in each harness.

## Supplied permission policy

Use the same runtime policy for both agents. The policy is **default deny**: anything not explicitly allowed is denied.

### Allowed

| Capability | Scope |
| --- | --- |
| Read | The task prompt, supplied skill, and assigned client file. |
| Edit | Only `starter/src/xyz_api_client.py`. |
| Local health request | Only the exact mock API health URL. |
| Local documentation request | Only the exact mock API documentation URL. |
| Syntax check | Only the supplied compile command for the assigned client. |
| Behavioral tests | Only the supplied test command in the assigned workspace. |
| Local API access during tests | Only the configured mock API origin. |

### Denied

| Capability | Reason |
| --- | --- |
| Public web search or fetch | The exercise must use the supplied local documentation. |
| Arbitrary URLs, `curl`, or `wget` commands | These could bypass the local-network boundary. |
| Arbitrary shell or Python commands | These could bypass file and network rules. |
| Package installation | Dependencies are already supplied. |
| Reading `mock_api/server.py` | The server source reveals the hidden API contract. |
| Reading the reference solution or hidden tests | These reveal the expected implementation. |
| Reading the other harness's workspace | Each harness must complete the task independently. |
| Writing outside the assigned client | Harness code, configuration, tests, and evidence must remain unchanged. |
| Destructive commands | They are unnecessary for this task. |
| Unknown tools or actions | Unspecified capabilities are denied by default. |

Every permission decision must be logged with the harness name, requested capability, allow or deny result, matched rule, and denial reason. Do not log secrets or full documentation responses.

A denial must be returned to the agent as a normal tool result. It must not terminate the agent loop.

## Task 2: Configure the hand-built Python loop

Use the extension points in the supplied loop to:

1. load the `xyz-api-client` skill;
2. register the syntax hook after client edits;
3. register the repeated-call hook before tool execution;
4. register the completion hook before the loop accepts completion;
5. apply the supplied permission policy before every tool call; and
6. write skill, hook, permission, and completion events to the run log.

Do not rewrite the loop. Add the supplied components through its existing interfaces.

Run the Python-loop integration tests:

```bash
python3 -m pytest tests/test_python_loop.py
```

Then run the API-client task with a fresh starter workspace:

```bash
python3 run_exercise.py --harness python
```

Save the generated client and run log.

## Task 3: Configure Hermes

Configure the supplied Hermes deployment to:

1. install or register the same `xyz-api-client` skill;
2. run the syntax hook after client edits;
3. run the repeated-call hook before tool execution;
4. run the completion hook before accepting completion;
5. enforce the same permission policy; and
6. capture equivalent skill, hook, permission, and completion events.

Use Hermes' native configuration where possible. If a supplied adapter is required, connect it without changing its behavior.

Run the Hermes integration tests:

```bash
python3 -m pytest tests/test_hermes.py
```

Then run the same API-client task from a separate fresh starter workspace:

```bash
python3 run_exercise.py --harness hermes
```

Save the generated client and run log.

## Task 4: Verify both harnesses

Run the shared verification suite:

```bash
python3 -m pytest tests/test_final_results.py
```

The supplied tests verify that both harnesses:

- loaded the skill;
- allowed required local operations;
- denied forbidden operations before execution;
- returned permission denials without crashing;
- ran the syntax hook after edits;
- blocked the sixth repeated tool call;
- ran the completion hook;
- produced separate completed clients; and
- passed the same API behavioral tests.

A harness does not pass merely because its final client works. Its log must also show that the required skill, hooks, and permissions were active.

## Task 5: Compare the harnesses

Submit a short report with this outcome table:

| Evidence | Python loop | Hermes |
| --- | --- | --- |
| Baseline smoke test | Pass or fail | Pass or fail |
| Integration tests | Pass or fail | Pass or fail |
| Skill loaded | Evidence from log | Evidence from log |
| Hook tests | Pass or fail | Pass or fail |
| Permission tests | Pass or fail | Pass or fail |
| Final client tests | Pass or fail | Pass or fail |
| Agent completed task | Yes or no | Yes or no |

Then answer these questions:

1. How did you register the skill in each harness?
2. How did you attach hooks to lifecycle events in each harness?
3. How did you express and enforce the permission policy?
4. Which harness required more integration code or configuration?
5. Which harness produced clearer errors and logs?
6. Which implementation would be easier to maintain, and why?

Support your answers with file references, test output, and run-log events. Do not choose a winner before running both implementations.

## Success criteria

You have completed the exercise when:

- [ ] both baseline harness tests pass before any integration changes;
- [ ] both live smoke tests return `HARNESS_OK`;
- [ ] both baseline result files are saved;
- [ ] the supplied skill is active in the Python loop;
- [ ] all three hooks are active in the Python loop;
- [ ] the Python loop enforces the supplied permission policy;
- [ ] the Python-loop integration tests pass;
- [ ] the Python-loop agent completes the API client;
- [ ] the supplied skill is active in Hermes;
- [ ] all three hooks are active in Hermes;
- [ ] Hermes enforces the supplied permission policy;
- [ ] the Hermes integration tests pass;
- [ ] the Hermes agent completes a separate copy of the API client;
- [ ] both final clients pass the shared behavioral tests; and
- [ ] your report explains the implementation differences using captured evidence.

## Expected exercise layout

```text
module-6-prod-harness/
├── exercise-prod-harness-starter/
│   ├── task.md
│   ├── starter/
│   │   └── src/
│   │       └── xyz_api_client.py
│   ├── python_loop/              # supplied hand-built loop
│   ├── hermes/                   # supplied Hermes deployment
│   ├── components/
│   │   ├── skill/                # supplied xyz-api-client skill
│   │   ├── hooks/                # supplied hook implementations
│   │   └── permissions/          # supplied policy
│   ├── tests/                    # supplied integration and behavior tests
│   ├── run_exercise.py
│   └── reports/
└── solution/
    ├── README.md
    ├── mock_api/server.py
    ├── src/xyz_api_client_solution.py
    ├── handbuilt_permissions.py
    ├── run_ablation.py
    ├── tests/
    └── reports/
```

The two measured agents must not have read access to the solution directory or to each other's workspaces.
