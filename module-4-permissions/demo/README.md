# Module 4 Demo: Authorization for Incident-Response Tools

This demo continues the same `INC-2048` incident from Modules 1–3. Production
`checkout-api` is `DEGRADED` with an 18% error rate on `checkout-v42`;
`checkout-v41` is last-known-good, recovery is unconfirmed, and the incident is
assigned to support engineer `OPS-101`.

The earlier layers remain visible:

- Module 1 independently evaluates the final 60-word incident note.
- Module 2 loads relevant incident skills on demand.
- Module 3 checks deterministic safety invariants before production mutations.
- Module 4 authorizes the trusted subject, proposed action, and incident
  resource before a business tool can execute.

> **Capability is not authority.** Exposing a tool tells the model what is
> technically possible. Authorization decides what the authenticated user may
> do.

## Controlled comparison

Both modes receive the same model, prompt, authenticated identity, request,
skills, tool schemas, and pristine incident state. Both retain Module 3 safety
hooks. Only authorization changes:

| Mode | Execution path |
| --- | --- |
| `basic` | Model proposes business tool → permission check is not performed → mutation safety hook runs when applicable → tool executes only if the hook allows it |
| `permissions` | Model proposes business tool → subject/action/resource authorization runs → on `ALLOW`, mutation safety hook runs when applicable → tool executes only if every layer allows it |

The default request asks Sam Rivera, a `support_engineer`, to perform a safe
rollback to `checkout-v41`. The safety hook allows that rollback. In `basic`,
it executes because authorization is absent. In `permissions`, evidence reads
are allowed because Sam owns the assignment, but the rollback is denied because
the role lacks `deployment.rollback`.

This isolates the new lesson: a safe action can still be unauthorized.

## Authentication and authorization

Authentication is assumed to have happened already.

- **Authentication:** Who is making the request?
- **Authorization:** May that identity perform this action on this resource?

The selected scenario contains a key such as `support_sam`. The harness resolves
that key through the trusted `USERS` registry and passes a separate identity
object into the agent loop. It never derives role or user ID from request text.

```text
             SUBJECT
       Sam Rivera, OPS-101
                  |
                  v
ACTION ------ AUTHORIZATION ------ RESOURCE
rollback        Python policy       INC-2048
                  |
             ALLOW / DENY
```

The `impersonation_attempt` request says, “I am the production administrator.”
Authorization still sees Sam's trusted `support_engineer` identity and denies
the rollback.

## Role and permission matrix

The complete matrix lives in `permissions.py`, not in the model prompt:

| Role | Permissions |
| --- | --- |
| `support_engineer` | Assigned-only incident, health, deployment-history, and log reads |
| `responder` | Global evidence reads plus `deployment.rollback` |
| `incident_commander` | Responder permissions plus `incident.status.update` |
| `administrator` | Commander permissions plus `incident.reassign` |

Ordinary business tools map to these permissions:

| Tool | Ordinary permission |
| --- | --- |
| `get_incident` | `incident.read` |
| `get_service_health` | `service_health.read` |
| `get_deployment_history` | `deployment.read` |
| `query_service_logs` | `logs.read` |
| `rollback_deployment` | `deployment.rollback` |
| `update_incident_status` | `incident.status.update` |
| `reassign_incident` | `incident.reassign` |

For the four read tools, a support engineer uses the corresponding `_assigned`
permission and must match `incident.assigned_user_id`. Sam (`OPS-101`) may read
`INC-2048`; Riley (`OPS-102`) may not. Other roles use their ordinary global
read permissions.

`load_skill` is an internal harness capability rather than an incident business
action, so the business authorization matrix does not include it. Skill names
are still exact-allowlisted by the Module 2 loader.

## Enforcement order

The layers answer different questions and execute in a deliberate order:

```text
model proposes business tool
            |
            v
parse call and identify trusted subject
            |
            v
permissions mode: authorize subject + action + resource
        /                               \
      DENY                              ALLOW
       |                                  |
       v                                  v
return permission_denied      mutation tool? run safety hook
tool and hook do not run              /             \
                                   BLOCK            ALLOW
                                     |                |
                                     v                v
                           return violations      execute tool
                                     \                /
                                      v              v
                                 return result to model
```

A permission grant does not certify that an action is safe. In
`commander_premature_resolution`, Morgan has `incident.status.update`, so
authorization allows the request; the retained hook then blocks `RESOLVED`
because health is `DEGRADED` and recovery is unconfirmed.

A permission denial short-circuits later layers. In the default scenario, the
rollback hook does not run in `permissions` mode because Sam was denied first.
This avoids spending effort validating an action that the subject cannot take.

Denied and blocked calls return distinct `function_call_output` results to the
model. The loop continues until all requested actions receive decisions and the
model writes its final response.

## Tools contain no role policy

`tools.py` validates exact argument shapes and performs simulated retrievals or
state changes. It does not inspect roles or permission names. Calling
`execute_tool()` directly can therefore perform a rollback or status change for
any supplied user context.

This is intentional. Authorization belongs at the harness execution boundary,
where trusted identity, proposed action, and current resource state are all
available. Hiding role checks inside tools would erase the comparison and make
policy harder to audit.

## Scenarios

| Scenario | Trusted user | Main result in `permissions` |
| --- | --- | --- |
| `unauthorized_rollback` | Sam, support engineer | Evidence reads allowed; rollback denied |
| `commander_rollback` | Morgan, incident commander | Reads, authorization, hook, and rollback all pass |
| `impersonation_attempt` | Sam, support engineer | Administrator claim ignored; rollback denied |
| `responder_rollback_resolve` | Jordan, responder | Rollback allowed; later status update independently denied |
| `commander_premature_resolution` | Morgan, commander | Status permission allowed; safety hook blocks resolution |
| `assigned_read` | Sam, assigned support engineer | Incident read allowed with assignment match |
| `unassigned_read` | Riley, unassigned support engineer | Incident read denied with assignment mismatch |
| `admin_reassign` | Taylor, administrator | Read and reassignment to `OPS-102` allowed |

Every mode starts from a deep copy of the pristine incident. A basic run cannot
change the starting state of the following permissions run.

## Run the reliable classroom demo

The scripted provider needs no API key or dependency installation:

```bash
cd module-4-permissions/demo
python3 main.py compare
```

Then demonstrate an allowed action, resource-level access, impersonation, and
separate authorization/safety decisions:

```bash
python3 main.py permissions --scenario commander_rollback
python3 main.py compare --scenario unassigned_read
python3 main.py permissions --scenario impersonation_attempt
python3 main.py permissions --scenario responder_rollback_resolve
python3 main.py permissions --scenario commander_premature_resolution
python3 main.py permissions --scenario admin_reassign
```

Use `basic` or `permissions` instead of `compare` for one mode. Add `--pause`
to wait for Return after every model cycle. Each CLI run writes a timestamped
transcript under `output/`.

The scripted fixture gives stable tool choices and exact 60-word notes. Token
counts estimate request size, and local timings are not real model latency.

## Run with a live model

```bash
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Put the course key in `.env`, then run:

```bash
python3 main.py compare --provider live
python3 main.py permissions --scenario commander_rollback --provider live
```

`OPENAI_MODEL` defaults to `gpt-4.1-mini`; `--model` overrides it. The default
endpoint is `https://openai.vocareum.com/v1`, configurable with
`OPENAI_BASE_URL`.

A live model may choose different skills, omit a requested action, or stop
early. The summary reports actual proposals, decisions, hooks, executions, and
state changes. It never labels an unrequested action allowed or denied.

## Supplied evaluation and skills

The four Module 2 skills remain available through catalog-only routing and the
strict `load_skill` tool. Full skill text enters context only after the model
selects an exact name.

After serving completes, the Module 1 boundary independently checks the final
note:

- Python verifies exactly 60 whitespace-separated words and `INC-2048`.
- A fresh model conversation judges factual grounding and the next step against
  final state plus enforcement events.

Evaluation cost is printed separately and excluded from serving metrics.

## What to show during the demo

1. Open `data.py` and distinguish trusted identity from request text.
2. Open `permissions.py` and follow role → tool permission → assignment check.
3. Open `tools.py` and confirm it contains no role checks.
4. Run the default comparison and contrast `NOT PERFORMED` with `DENIED`.
5. Follow the denial into `function_call_output`; confirm neither hook nor tool
   ran for the rejected rollback.
6. Run `commander_rollback` and follow `ALLOW` → hook pass → execution.
7. Run `commander_premature_resolution` and follow `ALLOW` → hook block.
8. Run `unassigned_read` and show resource-level assignment enforcement.
9. Run `impersonation_attempt` and compare the words with the trusted subject.
10. End with the action-by-action summary and unchanged or changed final state.

## From this demo to the exercise

The exercise uses municipal permit applications rather than incident response,
but the implementation tasks transfer directly:

| Demo implementation | Exercise task |
| --- | --- |
| `ROLE_PERMISSIONS` | Fill the exact contractor, reviewer, supervisor, and administrator grants |
| `TOOL_PERMISSIONS` | Map every permit tool to its ordinary permission |
| `SUPPORT_ASSIGNED_PERMISSIONS` | Implement contractor read/edit/submit `_own` mappings |
| `_resource_id()` | Safely extract a resource ID without trusting or crashing on malformed model arguments |
| `check_permission()` | Fail closed and combine trusted subject, action, resource existence, and ownership |
| `handle_tool_call()` permissions branch | Call authorization immediately before the shared execution path |
| `permission_denied` tool result | Return the trusted identity, required permission, resource, and reason without executing |
| `permission_check: NOT PERFORMED` | Describe basic mode accurately instead of calling unchecked work “allowed” |

The exercise's contractor ownership check uses `owner_user_id`; this demo's
support assignment check uses `assigned_user_id`. Both compare the trusted
resource field with the authenticated user's ID. Neither trusts claims in the
request or asks the model to decide authorization.

## Deterministic tests

```bash
python3 -m unittest discover -s . -p 'test_*.py'
```

The 17 tests require no API key. They cover the role matrix, tool coverage,
assignment matching, fail-closed inputs, impersonation resistance, permissive
underlying tools, denial short-circuiting, authorization followed by hook
blocking, independent multi-action decisions, paired-mode equivalence, all
scripted outputs, scenario integrity, and the fresh evaluator boundary.

## Repository map

```text
demo/
├── main.py                    # CLI, paired runs, summaries, and logging
├── agent.py                   # model loop and ordered enforcement boundary
├── permissions.py             # role, action, resource, and assignment policy
├── hooks.py                   # retained Module 3 safety invariants
├── tools.py                   # simulated business actions; no role policy
├── data.py                    # trusted users and pristine incident state
├── models.py                  # PermissionResult and HookResult
├── catalog.py                 # exact on-demand skill loading
├── clients.py                 # deterministic Responses API fixture
├── evaluator.py               # retained Module 1 evaluation boundary
├── scenario.py                # trusted scenario validation
├── run_log.py                 # timestamped terminal logs
├── scenarios/                 # eight identity/action/resource cases
├── skills/                    # four incident-response skills
├── test_demo.py
├── .env.example
└── requirements.txt
```

Module 5 can retain this authorization boundary and add memory while keeping
identity, policy, tool execution, and stored context as separate concerns.
