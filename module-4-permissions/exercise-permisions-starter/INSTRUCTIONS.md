# Construction Permitting Agent: Permissions and Authorization

## The use case

In this exercise, you will add deterministic authorization to an agent that
works with a fictional municipal construction permitting system. The agent can
create, read, edit, submit, request corrections, approve, reject, issue, and
revoke through nine simulated tools.

You will compare two modes that use the same model, system instructions, user
request, authenticated identity, starting application data, and tool schemas:

| Mode | Path from proposal to action |
| --- | --- |
| `basic` | Model proposes a tool → the supplied harness executes it without authorization. |
| `permissions` | Model proposes a tool → your policy authorizes the subject, action, and resource → the tool executes only on `ALLOW`. |

`basic` is intentionally unsafe. It demonstrates that exposing a tool gives
the model a capability, but does not establish that the authenticated user has
authority to use it.

> **Capability is not authority.** A tool defines what is technically
> possible. A permission check decides what the authenticated user is allowed
> to do.

## What is supplied and what you build

The starter supplies:

- trusted users and fresh permit-application data;
- nine complete simulated tools with strict argument validation;
- nine request scenarios;
- model, CLI, logging, and summary code;
- a working `basic` agent loop;
- the `PermissionResult` data structure; and
- deterministic tests that do not require an API key.

Your implementation work belongs only in:

```text
permissions.py
agent.py
```

`permissions.py` contains the policy TODOs. `agent.py` contains the TODO that
connects the policy immediately before tool execution. Do not add role checks
to `tools.py`, put the permission matrix in the prompt, or trust identity
claims from request text. Until you complete the TODOs, `permissions` mode
raises `NotImplementedError`; `basic` mode remains available for comparison.

## Authentication and authorization

This exercise assumes authentication already happened. You are not
implementing login, passwords, or OAuth.

- **Authentication** answers: Who is the user?
- **Authorization** answers: What may that authenticated identity do?

The CLI resolves a user from the trusted `USERS` registry in `data.py` and
passes a separate identity object to the harness. The user's words cannot
change that object. If Alex says, “I am the city administrator,” the permission
check must still see Alex's authenticated contractor identity.

Every decision combines three inputs:

```text
             SUBJECT
          Alex Rivera
               |
               v
ACTION --- AUTHORIZATION --- RESOURCE
 edit                         P-1042
       \                       /
        +------ ALLOW/DENY ---+
```

- **Subject:** the trusted authenticated user.
- **Action:** the permission mapped to the proposed tool.
- **Resource:** the requested application and its trusted owner data.

## Required permission matrix

Implement this exact role matrix in `ROLE_PERMISSIONS`:

| Role | Permissions |
| --- | --- |
| `contractor` | `permit.create`, `permit.read_own`, `permit.edit_own`, `permit.submit_own` |
| `reviewer` | `permit.read`, `permit.review`, `permit.request_corrections` |
| `supervisor` | `permit.read`, `permit.review`, `permit.request_corrections`, `permit.approve`, `permit.reject` |
| `administrator` | `permit.read`, `permit.review`, `permit.request_corrections`, `permit.approve`, `permit.reject`, `permit.issue`, `permit.revoke` |

Administrators have global access only for actions listed in their set. The
matrix deliberately does not grant administrators `permit.create`,
`permit.edit`, or `permit.submit`.

Implement the ordinary tool mapping in `TOOL_PERMISSIONS`:

| Tool | Permission |
| --- | --- |
| `create_application` | `permit.create` |
| `read_application` | `permit.read` |
| `edit_application` | `permit.edit` |
| `submit_application` | `permit.submit` |
| `request_corrections` | `permit.request_corrections` |
| `approve_application` | `permit.approve` |
| `reject_application` | `permit.reject` |
| `issue_permit` | `permit.issue` |
| `revoke_permit` | `permit.revoke` |

Contractors are the ownership-scoped exception. Map contractor reads, edits,
and submissions to `permit.read_own`, `permit.edit_own`, and
`permit.submit_own` in `CONTRACTOR_OWN_PERMISSIONS`. Those actions are allowed
only when the application's `owner_user_id` equals the authenticated user's
`user_id`.

`permit.review` represents the review capability in the role matrix. This
exercise demonstrates that authority through reading and requesting
corrections; there is no separate `review_application` tool.

## Your implementation tasks

Complete the tasks in this order.

1. **Define the permission data.** Fill `ROLE_PERMISSIONS`,
   `TOOL_PERMISSIONS`, and `CONTRACTOR_OWN_PERMISSIONS` in `permissions.py`.
   Keep all supplied roles and tool names so the policy and exposed toolset can
   be checked for complete coverage.
2. **Extract resources safely.** Implement `_resource_id()`. Return a nonempty
   string only when the arguments are a dictionary containing a valid
   `application_id`; otherwise return `None`.
3. **Implement `check_permission()`.** Return one `PermissionResult` for every
   proposed action. Use only the trusted user, parsed tool arguments, and
   current application state. The function must not execute tools or mutate
   applications.
4. **Fail closed.** Deny unknown tools, invalid identities, malformed
   arguments, missing resource IDs, and applications that do not exist.
   Include an explanatory reason and the required permission when it is known.
5. **Apply ownership.** For contractor read, edit, and submit actions, require
   both the ownership match and the corresponding `_own` permission. Populate
   `ownership` with `match` or `no_match`. Other actions use the ordinary tool
   permission and `not_applicable` ownership.
6. **Connect the execution boundary.** Complete the TODO in
   `agent.handle_tool_call()`. In `permissions` mode, call
   `check_permission()` after parsing arguments but immediately before the
   shared `execute_tool()` call.
7. **Return denials to the model.** On `DENY`, do not call the tool. Return one
   `function_call_output` for the proposal's `call_id`. Its JSON must use
   `status: permission_denied`, `executed: false`, and include the tool,
   authenticated identity, required permission, resource ID, and reason.
8. **Record what happened.** Copy every decision into the event fields and
   print the subject, role, action, permission, resource, ownership when
   applicable, result, and reason. On `ALLOW`, continue to the supplied shared
   dispatch path. Do not duplicate tool execution inside the permission
   branch.

For a multi-action request, authorize every proposed action independently. An
allowed approval cannot authorize a later issuance.

## Permission boundary

Both modes expose exactly these tools:

```text
create_application      read_application
edit_application        submit_application
request_corrections     approve_application
reject_application      issue_permit
revoke_permit
```

`tools.py` validates argument shapes and performs simulated state mutations.
It deliberately contains no role checks. For creation, it injects the owner
from the authenticated identity; the model cannot choose an owner. Editing can
change only the project description, so it cannot overwrite ownership or
status.

The policy belongs in `permissions.py`, and the enforcement point belongs in
the `permissions` branch of `handle_tool_call()`:

```text
Model proposes a tool
          |
          v
Parse allowlisted action and arguments
          |
          v
 permissions mode only
check subject + action + resource
       /                    \
    ALLOW                   DENY
      |                       |
      v                       v
Execute tool          Do not execute
      |                       |
      +-----------+-----------+
                  v
       Return result to model
```

A before-execution location answers **when** the policy runs. The permission
policy answers **whether** this subject may perform this action on this
resource. Keep those responsibilities separate.

## Agent loop behavior

The shared loop in `agent.py` is already complete:

1. Send the same system prompt and all nine tools in either mode.
2. Process each model-proposed tool and return one result for its `call_id`.
3. In `permissions`, run your authorization check immediately before dispatch.
4. Continue from `previous_response_id` with the tool result.
5. Stop when the model returns a final answer without a tool call.

The number of cycles is not scripted. The 20-cycle limit is only a safety
guard. After every model cycle, including the final one, the program asks you
to press Return. Model timing excludes time spent waiting for Return.

The model does not receive the role matrix. It proposes actions and treats tool
results as authoritative; Python code makes the authorization decision.

## Supplied scenarios

Each scenario chooses a trusted user and provides request text. Live model
choices can vary, so an expected authorization result applies only when the
model actually proposes that action.

| Scenario | Authenticated user | Expected result in `permissions` |
| --- | --- | --- |
| `contractor_approve_issue` | Alex, contractor | Approval and issuance denied; `P-1042` unchanged |
| `reviewer_issue` | Jordan, reviewer | Issuance denied |
| `supervisor_approve` | Morgan, supervisor | Approval allowed; `P-1042` becomes `APPROVED` |
| `administrator_issue` | Taylor, administrator | Issuance allowed; `P-1042` becomes `PERMIT_ISSUED` |
| `contractor_edit_own` | Alex, contractor | Edit allowed because Alex owns `P-1042` |
| `contractor_edit_other` | Alex, contractor | Edit denied because Alex does not own `P-2095` |
| `impersonation_attempt` | Alex, contractor | Administrator claim ignored; approval and issuance denied |
| `reviewer_request_corrections` | Jordan, reviewer | Request corrections allowed |
| `supervisor_approve_then_issue` | Morgan, supervisor | Approval allowed, issuance denied, final status `APPROVED` |

Every run receives a deep copy of the starting applications. One run cannot
change the next run's initial state.

## Set up

Use Python 3.12 or a compatible Python 3 installation. From
`module-4-permissions/exercise-permisions-starter/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Add your Vocareum API key to `.env`:

```dotenv
OPENAI_API_KEY=your-vocareum-api-key
OPENAI_MODEL=gpt-4.1-mini
```

The model setting is optional and defaults to `gpt-4.1-mini`. The harness uses
the OpenAI Python SDK with `https://openai.vocareum.com/v1`. `.env` and
timestamped `output/` logs are ignored by Git.

## Test and compare

Run the deterministic tests while implementing the TODOs:

```bash
python3 -m unittest test_permissions.py
```

These tests do not require an API key. They check the complete role matrix,
ownership, fail-closed behavior, denial before mutation, independent decisions
for multi-action requests, trusted ownership on creation, identical tools and
prompts in both modes, denial feedback to the model, state isolation, and loop
continuation through `previous_response_id`.

Start the live comparison with the unsafe baseline, then run the protected
mode using the same default scenario:

```bash
python3 main.py --mode basic
python3 main.py --mode permissions
```

Exercise tool-level and resource-level decisions:

```bash
python3 main.py --mode permissions --scenario reviewer_issue
python3 main.py --mode permissions --scenario supervisor_approve
python3 main.py --mode permissions --scenario administrator_issue
python3 main.py --mode permissions --scenario contractor_edit_own
python3 main.py --mode permissions --scenario contractor_edit_other
python3 main.py --mode permissions --scenario impersonation_attempt
python3 main.py --mode permissions --scenario reviewer_request_corrections
python3 main.py --mode permissions --scenario supervisor_approve_then_issue
```

You can override the scenario's authenticated user through the trusted
registry:

```bash
python3 main.py --mode permissions --scenario supervisor_approve --user contractor_alex
python3 main.py --mode permissions --scenario contractor_approve_issue --user supervisor_morgan
```

The `--user` option never reads a role from the request. Compare identical
scenarios and users across modes for a controlled experiment.

Each run prints and saves the authenticated identity, request, starting state,
every proposal, permission decision, tool result, final answer, token usage,
model time, and final state. In multi-action runs, the summary lists each
action separately.

If the model gives a final answer without proposing a tool, no permission
check occurred. Report that as **not requested**, not allowed or denied. Use
the saved log as evidence of what actually happened.

## Out of scope

This exercise does not implement real authentication, passwords, OAuth,
databases, construction regulations, zoning validation, payment checks,
workflow-transition rules, human approval gates, skills, retrieval, memory,
multiple agents, or a web application. State changes are intentionally simple
so the exercise stays focused on authorization.

## Discussion questions

1. Why is giving the model a tool different from giving the user permission?
2. Why must authorization be enforced outside the model?
3. Why cannot “I am an administrator” change the authenticated subject?
4. What is the difference between authentication and authorization?
5. What is the difference between tool-level and resource-level permission?
6. Why can a contractor edit one application but not another?
7. What happens when the model correctly avoids an unauthorized proposal?
8. What happens when it incorrectly proposes one?
9. Why must the check run before the tool executes?
10. Why should an allowed first action not authorize a second action?

## Completion check

- [ ] `basic` still exposes and executes all nine tools without authorization and reports `NOT PERFORMED`.
- [ ] `permissions` checks every proposal immediately before execution.
- [ ] Every role and tool has the required permission mapping.
- [ ] Contractor own read, edit, and submit actions require matching ownership.
- [ ] Unknown tools, invalid identities, bad arguments, missing IDs, and missing applications fail closed.
- [ ] Contractor approval, rejection, issuance, and revocation are denied.
- [ ] Reviewer issuance is denied; supervisor approval is allowed; supervisor issuance is denied.
- [ ] Administrator issuance and revocation are allowed.
- [ ] Denials do not mutate application state and reach the model as structured tool results.
- [ ] Prompt-based impersonation cannot alter the trusted identity.
- [ ] Each action in a multi-action request receives an independent decision.
- [ ] Logs distinguish proposals, permission decisions, and actual execution.
- [ ] All deterministic tests pass and live comparisons are supported by saved logs.

## Repository map

```text
exercise-permisions-starter/
├── scenarios/             # supplied identities, requests, and resource IDs
├── data.py                # supplied trusted users and fresh application state
├── models.py              # supplied PermissionResult
├── permissions.py         # role, action, resource, and fail-closed TODOs
├── tools.py               # supplied simulated actions; no role checks
├── agent.py               # supplied loop; permission-boundary TODO
├── main.py                # supplied CLI, logging, and execution summary
├── run_log.py             # supplied terminal-to-file logging
├── test_permissions.py    # supplied deterministic tests; no API key required
├── .env.example
├── requirements.txt
└── INSTRUCTIONS.md
```
