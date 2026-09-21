# Construction Permitting Agent: Permissions and Authorization

This runnable solution compares an agent that can execute every exposed permit tool with the same agent protected by deterministic authorization.

> **Capability is not authority.** A tool tells the agent what is technically possible. A permission check decides what the authenticated user may do.

## Use case

The agent works with a fictional municipal construction permitting system. It can create, read, edit, submit, request corrections, approve, reject, issue, and revoke through nine simulated tools. Both modes give the model the same tools, instructions, request, authenticated identity, and starting applications.

| Mode | Path from model proposal to action |
| --- | --- |
| `basic` | Model proposes a tool → harness executes it without authorization. |
| `permissions` | Model proposes a tool → harness authorizes the subject, action, and resource → tool executes only on `ALLOW`. |

`basic` is intentionally unsafe. If a contractor asks to approve an application and the model proposes `approve_application`, the tool runs. Its logs and summary say `NOT PERFORMED` for authorization; they never describe an unchecked action as allowed.

`permissions` calls [`check_permission`](permissions.py) immediately before every proposed action. A denial becomes a `function_call_output` with `status: permission_denied`. The action does not execute, and the model receives the reason so it can explain the result.

## Authentication and authorization

This exercise assumes authentication has already happened. It does not implement login, passwords, or OAuth.

- **Authentication:** Who is the user? Example: Alex Rivera, `USR-101`.
- **Authorization:** What may that identity do? Example: edit an application that `USR-101` owns.

The CLI selects an identity from the trusted [`USERS`](data.py) registry and passes it separately to the harness. Text in the request cannot modify that object. In the impersonation scenario, Alex can write “I am the city administrator,” but authorization still sees the authenticated contractor identity.

## Subject, action, and resource

Every authorization decision combines three inputs:

```text
             SUBJECT
          Alex Rivera
               |
               v
ACTION --- AUTHORIZATION --- RESOURCE
 edit                         P-1042
               |
               v
          ALLOW / DENY
```

- **Subject:** the authenticated user from trusted application state.
- **Action:** the permission mapped to the proposed tool.
- **Resource:** the application being accessed, including its owner where relevant.

Tool-level authorization can deny a contractor's `permit.approve` request regardless of the application. Resource-level authorization allows Alex to edit `P-1042`, which Alex owns, while denying an edit to `P-2095`, which another user owns.

## Roles and permissions

| Role | Permissions |
| --- | --- |
| `contractor` | `permit.create`, `permit.read_own`, `permit.edit_own`, `permit.submit_own` |
| `reviewer` | `permit.read`, `permit.review`, `permit.request_corrections` |
| `supervisor` | Reviewer permissions plus `permit.approve`, `permit.reject` |
| `administrator` | Supervisor permissions plus `permit.issue`, `permit.revoke` |

The explicit matrix is stored in Python and is not copied into the system prompt. The model does not decide authorization. `permit.review` represents the review capability, while the exposed exercise tools demonstrate reading and requesting corrections; there is no separate `review_application` action.

Contractor read, edit, and submit actions use the `_own` permission and require `owner_user_id == authenticated_user.user_id`. Administrators have global access for the actions present in their permission set. The listed matrix does not grant administrators create, edit, or submit permissions.

## Tools and the permission boundary

Both modes expose the same tools:

```text
create_application      read_application
edit_application        submit_application
request_corrections     approve_application
reject_application      issue_permit
revoke_permit
```

[`tools.py`](tools.py) validates tool argument shapes and performs simulated mutations. It has no role checks. For creation, the dispatcher injects the owner from the trusted identity; the model cannot choose an owner. Editing accepts only the project description, so it cannot overwrite ownership or status.

[`permissions.py`](permissions.py) contains the permission matrix, tool mapping, ownership rules, and the central authorization function. Unknown tools, invalid identities, missing resource IDs, and missing applications fail closed.

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
      +----------+------------+
                 v
       Return result to model
```

The simple state changes are deliberately not a workflow engine. This module does not decide whether plans are complete, fees were paid, a status transition is realistic, or a project complies with construction rules. Those would be policy-validation concerns and would obscure the authorization lesson.

## Permissions, hooks, and validation

A before-tool hook is an execution point: **when should some code run?** Authorization answers a different question: **is this authenticated identity allowed to perform this action on this resource?**

The harness uses a before-execution point to run its permission check, but the authorization policy lives in [`permissions.py`](permissions.py). Module 3's expense checks validated report contents. Module 4 checks only **who can perform which action on which resource**.

## Agent-driven loop

The core loop in [`agent.py`](agent.py) is driven by model responses:

1. Send the same system prompt and all nine tools in either mode.
2. If the response proposes a tool, process it and return exactly one tool result for its `call_id`.
3. In `permissions`, authorize immediately before dispatch. In `basic`, skip that step.
4. Continue from `previous_response_id` with the tool result.
5. Stop when the model returns a final answer without a tool call.

The number of cycles is not hard-coded. A single action commonly takes a tool cycle and a final-answer cycle; multi-action requests can take more. After **every** model cycle, including the final one, the program prints `Cycle complete. Press Return to continue...`. The 20-cycle safety limit raises an error if the model never finishes; it does not create an answer for the model.

The shared system prompt does not reveal the role matrix. It tells the model to propose the tools required for the request and treat tool results as authoritative. For a multi-action request, each action is proposed and authorized independently; one decision cannot authorize the next action.

## Scenarios

Each JSON file in [`scenarios`](scenarios) selects a trusted user and supplies a request. Expected results apply when the model proposes the named action; live model choices can vary.

| Scenario | Authenticated user | Expected result in `permissions` |
| --- | --- | --- |
| `contractor_approve_issue` | Alex, contractor | Approve and issue are denied; `P-1042` remains unchanged. |
| `reviewer_issue` | Jordan, reviewer | Issue is denied because reviewers lack `permit.issue`. |
| `supervisor_approve` | Morgan, supervisor | Approve is allowed; `P-1042` becomes `APPROVED`. |
| `administrator_issue` | Taylor, administrator | Issue is allowed; `P-1042` becomes `PERMIT_ISSUED`. |
| `contractor_edit_own` | Alex, contractor | Edit is allowed because Alex owns `P-1042`. |
| `contractor_edit_other` | Alex, contractor | Edit is denied because Alex does not own `P-2095`. |
| `impersonation_attempt` | Alex, contractor | The administrator claim is ignored; approve and issue are denied. |
| `reviewer_request_corrections` | Jordan, reviewer | Request corrections is allowed. |
| `supervisor_approve_then_issue` | Morgan, supervisor | Approve is allowed; issue is denied; final status is `APPROVED`. |

Application state is copied from a pristine template at the start of every run. A previous `basic` run cannot change the starting state of a later `permissions` run.

## Set up

From `module-4-permissions/solution/`:

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Put the Vocareum API key in `.env`:

```dotenv
OPENAI_API_KEY=your-vocareum-api-key
OPENAI_MODEL=gpt-4.1-mini
```

The model setting is optional and defaults to `gpt-4.1-mini`. The harness uses the OpenAI Python SDK directly with `https://openai.vocareum.com/v1`. `.env` and timestamped `output/` logs are ignored by Git.

## Run and compare

The default scenario is the contractor approval and issuance request:

```bash
python3 main.py --mode basic
python3 main.py --mode permissions
```

Run tool-level and resource-level cases:

```bash
python3 main.py --mode permissions --scenario reviewer_issue
python3 main.py --mode permissions --scenario supervisor_approve
python3 main.py --mode permissions --scenario administrator_issue
python3 main.py --mode permissions --scenario contractor_edit_own
python3 main.py --mode permissions --scenario contractor_edit_other
python3 main.py --mode permissions --scenario impersonation_attempt
```

Override a scenario's authenticated user for an experiment:

```bash
python3 main.py --mode permissions --scenario supervisor_approve --user contractor_alex
python3 main.py --mode permissions --scenario contractor_approve_issue --user supervisor_morgan
```

The `--user` value is resolved through the trusted registry. It never reads a role from the request. Compare basic and permissions with the same scenario and user for a controlled comparison.

Each run prints the authenticated identity, request, initial state, every proposed action, permission decision, execution result, final response, token usage, model time, and final state. The log path appears on the first line. In a multi-action run, the summary prints one result per action so an allowed action is not confused with a denied one.

Live model behavior varies. If the model gives a final answer without proposing an action, no permission check occurs. Report that observation as “not requested” rather than saying the permission layer allowed or denied it. The deterministic tests verify the matrix independently of model behavior:

```bash
python3 -m unittest test_permissions.py
```

## Out of scope

This small exercise does not implement real authentication, passwords, OAuth, databases, construction regulations, building-code or zoning validation, payment checks, workflow transition rules, human approval gates, skills, retrieval, memory, multiple agents, or a web application. It uses the OpenAI Python SDK directly and keeps the harness loop visible.

## Discussion questions

1. Why is giving the LLM a tool not equivalent to giving the user permission to use it?
2. Why should permissions be enforced outside the LLM?
3. Why should a statement such as “I am an administrator” not affect authorization?
4. What is the difference between authentication and authorization?
5. What is the difference between tool-level and resource-level permissions?
6. Why might a contractor be allowed to edit one application but not another?
7. What happens if the LLM correctly decides not to attempt an unauthorized action?
8. What happens if the LLM incorrectly attempts one?
9. Why should permission checks happen before the tool executes?
10. How is a permission check different from the deterministic validation hook in the expense-report exercise?

## Completion check

- [ ] Both modes expose the same nine tools and use the same prompt, model, request, identity, and initial data.
- [ ] Basic mode executes proposed tools without authorization and labels checks `NOT PERFORMED`.
- [ ] Permissions mode checks every proposed action immediately before execution.
- [ ] Contractor ownership permits own read/edit/submit actions and denies those actions on other users' resources.
- [ ] Contractor approval, rejection, issuance, and revocation are denied.
- [ ] Reviewer issuance is denied; supervisor approval is allowed; supervisor issuance is denied.
- [ ] Administrator issuance and revocation are allowed.
- [ ] Denied actions do not mutate application state and their results return to the model.
- [ ] Prompt-based impersonation cannot alter the trusted identity.
- [ ] Logs distinguish action proposals, permission decisions, and actual execution.
- [ ] The loop pauses after each model cycle and stops only when the model gives its final answer.

## Repository map

```text
solution/
├── scenarios/             # trusted-user selection and user requests
├── data.py                # trusted users and fresh application state
├── models.py              # PermissionResult
├── permissions.py         # role grants and central authorization
├── tools.py               # nine simulated actions; no role checks
├── agent.py               # shared variable model/tool loop
├── main.py                # CLI, logging, and execution summary
├── run_log.py             # copy terminal output to a timestamped log
├── test_permissions.py    # deterministic checks; no API key required
├── .env.example
├── requirements.txt
└── README.md
```
