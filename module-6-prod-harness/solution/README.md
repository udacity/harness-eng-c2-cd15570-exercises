# Production Harnesses with Hermes: The Offline API Connector

In the previous modules, you built the major parts of an agent harness yourself: the model loop, skills, hooks, permissions, and evaluation. In this module, you will decide which of those responsibilities can move into a production agent harness.

You will use Hermes to run an agent, control its tool access, execute lifecycle hooks, and collect evidence about its behavior. You will then compare those built-in capabilities with equivalent controls written in Python.

> **Your goal is to decide where a production harness is sufficient and where application-specific code is still necessary.**

## Scenario

You need an agent to write a Python client for the fictional **2026 XYZ API**. This API is newer than the information available to the model, so the agent cannot safely rely on remembered authentication schemes, endpoints, headers, or payload formats.

A local mock service represents the current API. It provides:

- a health endpoint;
- a documentation endpoint;
- a data synchronization operation;
- deterministic success and error responses.

The exact client specification is intentionally omitted here. The agent must recognize its knowledge gap and discover the specification from the service.

External web access may be denied during the exercise. A denial should not crash the session. The agent should treat it as new information, revise its plan, and use the allowed local documentation instead.

## Run the local API

Open a terminal and start the mock API from the solution directory:

```bash
cd module-6-prod-harness/solution
python3 mock_api/server.py
```

The server listens at:

```text
http://localhost:8080
```

Confirm that it is running from another terminal:

```bash
curl http://localhost:8080/health
```

Keep the server terminal running while you use Hermes or execute the connector. Press `Ctrl+C` in that terminal to stop the server.

## What you will learn

By completing this exercise, you will be able to:

1. **Configure a production agent harness.** Define tool access and lifecycle enforcement through Hermes instead of rebuilding the entire agent loop.
2. **Handle permission denials inside an agent workflow.** Return a clear denial to the agent so it can choose another path.
3. **Place controls at the correct lifecycle point.** Distinguish permission checks, before-tool hooks, after-tool hooks, and session completion hooks.
4. **Use deterministic hooks for deterministic rules.** Check Python syntax, unsafe content, and repeated tool calls with code.
5. **Separate structural checks from behavioral evaluation.** Recognize that valid Python can still call an API incorrectly.
6. **Compare prebuilt and custom harness components.** Evaluate configuration effort, enforcement, recovery, runtime overhead, and control.
7. **Use ablations to support architecture decisions.** Remove one component at a time and measure what changes.

## Why this task needs a harness

The agent can produce a Python file that compiles while still using an outdated API pattern. It might:

- choose an obsolete authentication method;
- call the wrong endpoint;
- omit a required version or identity header;
- send the wrong JSON structure;
- continue retrying a tool after access has been denied;
- claim success without running the behavioral tests.

A syntax check can catch malformed Python. It cannot prove that the connector follows the current API contract.

You will combine several forms of evidence:

- permission decisions show which capabilities were available;
- hook events show which deterministic checks ran;
- the session trace shows how the agent adapted;
- behavioral tests show whether the client actually works;
- a read-only evaluator identifies unsupported assumptions and explains failures.

## Harness flow

```text
Your task
    |
    v
Hermes agent loop
    |
    +---- permission decision
    |       |
    |       +---- allow: execute the tool
    |       +---- ask: request approval
    |       +---- deny: return the denial to the agent
    |
    +---- lifecycle hooks
    |       |
    |       +---- validate changed Python
    |       +---- inspect untrusted content
    |       +---- detect repeated tool calls
    |       +---- record session completion
    |
    v
Candidate API client
    |
    +---- structural checks
    +---- behavioral tests against the mock API
    +---- read-only evaluation
    |
    v
Measured comparison report
```

The model chooses its next action from the evidence it receives. The harness constrains and observes those choices without forcing a fixed number of cycles.

## Your exercise objectives

You will complete the exercise in five stages.

### 1. Configure Hermes permissions

Create a small, reviewable policy for the tools needed by the task.

| Capability | Expected policy | Why |
| --- | --- | --- |
| Read exercise files | Allow | The agent must inspect the task and existing code. |
| Edit the assigned client | Allow | The agent must implement the connector. |
| Run Python and the supplied tests | Allow | The agent needs local validation. |
| Access the local service and documentation | Allow | This is the current source of API truth. |
| Search or fetch from the public web | Ask or deny for selected runs | This creates the recovery scenario. |
| Install packages | Ask | Installation changes the environment and may use the network. |
| Destructive filesystem commands | Deny | They are unnecessary for the task. |

Permissions answer whether the agent may use a capability. They do not determine whether the resulting client is correct.

### 2. Configure lifecycle hooks

Implement hooks with distinct responsibilities:

1. **Python validation:** compile the client after a write or edit and return any syntax error immediately.
2. **Untrusted-content guard:** inspect external tool results before the agent treats their contents as instructions or code.
3. **Repetition gate:** detect equivalent repeated tool calls and stop an unproductive loop after a documented threshold.
4. **Session record:** capture the final status and hook activity needed for evaluation.

Each hook must consume real runtime input and produce an observable result. A placeholder command that only prints a message is not an implemented hook.

### 3. Run the connector task

Give the agent the API connector task without supplying the hidden API specification. Observe whether it:

1. recognizes that its API knowledge may be incomplete;
2. looks for current documentation;
3. handles an external-access denial;
4. discovers the allowed local documentation;
5. implements the client from retrieved evidence;
6. runs the behavioral tests;
7. corrects failures using tool and test output;
8. stops after producing a verified client.

The completed client must include explicit timeouts, structured response handling, and useful error handling. The behavioral tests will verify the exact API contract.

### 4. Compare Hermes with custom Python

Run the same connector task through two harness implementations.

| Approach | Responsibility |
| --- | --- |
| Hermes | Provides the agent loop, tool permissions, lifecycle hooks, tool results, and session events. |
| Hand-built Python | Implements equivalent boundaries directly so you can compare effort and expressiveness. |

Keep the task, starting client, mock API, tests, prompt, and success criteria constant. A useful comparison changes one harness boundary at a time.

Use the comparison to answer questions such as:

- How much code and configuration does each approach require?
- Does each approach return a usable denial to the agent?
- Can each approach inspect or transform tool content?
- Can each approach maintain state across repeated calls?
- Which approach makes the enforcement trace easier to audit?

### 5. Run controlled ablations

Evaluate these configurations:

| Configuration | Purpose |
| --- | --- |
| `hermes-full` | Hermes permissions and hooks are enabled. |
| `hermes-no-hooks` | Shows what changes when lifecycle enforcement is removed. |
| `hermes-web-denied` | Tests recovery through allowed local documentation. |
| `handbuilt-full` | Runs equivalent controls through custom Python. |
| `unprotected` | Establishes behavior without the harness controls. |

Record the following evidence for every run:

- completion status;
- behavioral test result;
- model and tool cycles;
- permission requests and denials;
- hook executions and blocks;
- repeated-call termination;
- model and wall-clock time when available;
- final client artifact;
- evaluator findings.

Measure latency, catch rates, cycles, and evaluator accuracy from the captured runs. Do not insert assumed values into the report.

## Evaluation

### Deterministic checks

The behavioral test suite verifies observable client behavior, including:

- the client exists and imports;
- the connection function returns structured data;
- the request reaches the correct operation;
- authentication and required headers are correct;
- the request body follows the documented structure;
- the success response is parsed correctly;
- documentation discovery uses an allowed source.

These tests are the execution oracle. A plausible explanation from the model cannot turn a failing request into a successful connector.

### Read-only evaluator

The evaluator may inspect:

- the original task;
- the final client source;
- behavioral test output;
- the permission and hook trace;
- the agent's final explanation.

The evaluator may identify unsupported assumptions, missing evidence, or a mismatch between the source and the agent's claims. It must not edit the client or replace the deterministic test result.

## Completion checklist

- [ ] You can run the connector task through Hermes.
- [ ] External web denial returns a controlled result instead of crashing the session.
- [ ] The agent recovers by consulting the allowed local documentation.
- [ ] The generated client passes every behavioral test.
- [ ] The syntax hook catches an intentionally malformed edit.
- [ ] The content guard blocks a known unsafe fixture and permits a safe fixture.
- [ ] The repetition gate stops equivalent repeated calls at the documented limit.
- [ ] Session logs identify which permissions and hooks ran.
- [ ] The hand-built comparison uses the same task and acceptance tests.
- [ ] The ablation report is generated from captured executions.
- [ ] Your conclusion explains where Hermes is sufficient and where custom code adds necessary control.

## Discussion questions

1. What should the agent do when it recognizes that its API knowledge may be outdated?
2. Why should a permission denial be returned to the model instead of ending the process?
3. Which controls belong before a tool call, after a tool call, or after the session?
4. Why is successful compilation insufficient evidence that an API connector works?
5. When does a prebuilt hook reduce maintenance burden?
6. When does application-specific Python provide meaningfully better control?
7. How can a repetition gate stop waste without forcing every task to use the same number of cycles?
8. What evidence would justify keeping or removing each harness component?

## Solution files

```text
solution/
├── README.md                     # this exercise guide
├── .hermes/settings.json         # Hermes hooks and permissions
├── mock_api/                     # local 2026 XYZ API
├── src/
│   └── xyz_api_client_solution.py
├── handbuilt_permissions.py      # custom harness comparison
├── run_ablation.py               # controlled experiment runner
├── tests/                        # behavior and harness checks
└── reports/                      # generated run evidence
```
