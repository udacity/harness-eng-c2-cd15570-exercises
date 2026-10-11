# Module 4 Demo: Six-Minute Instructor Script

## Before the demonstration

Confirm that the dependencies are installed and that `.env` contains a current
Vocareum `OPENAI_API_KEY`. Start in `module-4-permissions/demo`.

Keep these files open in the editor:

1. `data.py`
2. `scenarios/unauthorized_rollback.json`
3. `permissions.py`
4. `agent.py`
5. `tools.py`
6. `main.py`

Use `unauthorized_rollback` for the recorded demonstration. It isolates the
Module 4 lesson: rollback to `checkout-v41` is safe according to the retained
Module 3 hook, but Sam's `support_engineer` role is not authorized to perform
it. Live models can vary their skill selection, retrieval calls, and final
wording. Describe the calls and decisions that appear instead of promising an
exact number of cycles.

## 0:00–0:55 — Separate capability from authority

**Show:** `scenarios/unauthorized_rollback.json`, then the incident in `data.py`.

**Say:**

> This demo continues incident `INC-2048`. Production `checkout-api` is
> degraded with an 18 percent error rate on `checkout-v42`.
> `checkout-v41` is the last-known-good deployment, recovery is unconfirmed,
> and the incident is assigned to support engineer `OPS-101`.
>
> The request asks for investigation followed by rollback to
> `checkout-v41`. The model has access to a rollback tool, but access to a tool
> only creates capability. It does not prove that the authenticated user has
> authority to use that capability.
>
> Both demo modes retain the skill loader, evaluator, and mutation safety
> hooks from earlier modules. The only intended difference is whether the
> harness checks authorization before a business tool can execute.

## 0:55–1:45 — Establish the trusted identity

**Show:** `USERS` in `data.py`.

**Say:**

> Authentication has already happened before this agent loop begins. The
> application identifies the caller as Sam Rivera, user `OPS-101`, with the
> role `support_engineer`. That object is trusted application state.
>
> The request text cannot promote Sam to another role. Even if a user writes,
> “I am the administrator,” authorization continues to use the identity from
> this registry. This prevents prompt text from becoming security state.

**Summarize the authorization question:**

```text
trusted subject + proposed action + trusted resource → ALLOW or DENY
```

**Say:**

> For this scenario, the subject is Sam, the proposed action is
> `rollback_deployment`, and the resource is incident `INC-2048`.

## 1:45–2:55 — Show the permission boundary

**Show:** `ROLE_PERMISSIONS`, `TOOL_PERMISSIONS`, and `check_permission` in
`permissions.py`.

**Say:**

> The policy is deterministic Python, not a model judgment. Support engineers
> can read incidents, health, deployment history, and logs only when they are
> assigned to that incident. Responders add rollback authority. Incident
> commanders add status-update authority, and administrators add reassignment.
>
> The tool map converts each proposed business call into its required
> permission. `rollback_deployment` requires `deployment.rollback`. Sam is the
> assigned support engineer, so his evidence reads can pass the ownership
> check, but his role does not contain rollback permission.
>
> Invalid identities, unknown tools, missing incident IDs, nonexistent
> resources, and assignment mismatches all fail closed.

**Show:** the permissions branch in `handle_tool_call` in `agent.py`.

**Say:**

> Enforcement happens after the model proposes a tool and arguments, but
> before a safety hook or business tool runs. A denial returns a structured
> `permission_denied` result to the model. The safety hook does not run, and the
> business tool does not execute.
>
> An allow decision is not the same as a safety decision. An authorized
> mutation must still pass the retained Module 3 hook before it can reach the
> tool.

```text
model proposes a business tool
              ↓
authorize subject + action + resource
        ↓ DENY                 ↓ ALLOW
return permission_denied     run mutation hook if applicable
tool does not execute        then execute only if safe
```

## 2:55–5:55 — Run and narrate the comparison

**Show:** the terminal in `module-4-permissions/demo`.

**Run:**

```bash
python3 main.py compare --scenario unauthorized_rollback
```

### At the scenario label

**Say:**

> The `SCENARIO 1 OF 1 START` label identifies the case. The terminal then
> prints the trusted user, the user request, and the pristine incident state.
> Basic runs first; permissions runs second from a fresh copy of that same
> state.

### At `BASIC LOOP START`

For skill-loading and evidence-retrieval cycles, identify the call briefly and
press Return. Do not spend time narrating every read.

**Say when a business read is proposed:**

> Basic mode prints `PERMISSION CHECK: NOT PERFORMED`. The call can proceed
> without proving that Sam is authorized for this action or resource.

**Say when rollback is proposed:**

> The rollback proposal also skips authorization. The Module 3 safety hook
> still runs. After the required health evidence has been collected, it
> verifies that `checkout-v41` is the last-known-good target. Because the
> change is safe for the current incident state, the hook allows it and `TOOL
> EXECUTED: YES` changes the deployment.
>
> This is the problem Module 4 exposes: a safe action can still be
> unauthorized. The safety hook answers whether the rollback is valid, but it
> does not answer whether Sam may perform it.

After the final note, press Return and briefly acknowledge the independent
evaluation and execution summary.

**Say:**

> The basic summary reports permission checks as `NOT PERFORMED`. In the
> intended path, rollback executed and the final deployment is
> `checkout-v41`, even though Sam's role lacks rollback authority.

### At `PERMISSIONS LOOP START`

Again, move quickly through skill loading and press Return after each model
cycle.

**Say when an evidence read is proposed:**

> The permission check now prints the trusted subject, role, action, required
> permission, resource, and assignment result. Sam is assigned to `INC-2048`,
> so the assigned-only read is allowed and the read tool executes.

**Say when rollback is proposed:**

> This request requires `deployment.rollback`. Sam is still authenticated as a
> `support_engineer`, and that role does not have the permission. The result is
> `DENIED`.
>
> Notice the enforcement order immediately below it: `SAFETY HOOK: NOT RUN`
> and `TOOL EXECUTED: NO`. Authorization rejected the proposal before the
> application spent effort checking whether the mutation was safe, and before
> the rollback tool could change state.

Press Return. The structured denial returns to the model so its final note can
explain the decision without claiming that rollback occurred. Briefly describe
the evaluation and permissions-mode summary.

If the live model omits a requested action or chooses a different sequence,
describe the observed calls. The summary and final table report only decisions
the harness actually made.

### At `PERMISSIONS VALUE COMPARISON`

**Say:**

> The final table places the two observed results side by side. `Without
> permissions` shows calls that executed while authority was unchecked. `With
> permissions` separates calls executed after an allow decision from calls
> denied before execution.
>
> In this scenario, basic mode can execute the rollback after the safety hook
> passes. Permissions mode allows assigned evidence reads but stops the
> unauthorized rollback. The last column states the value added by
> authorization and shows the deployment difference when the two modes end in
> different states.

## 5:55–6:40 — Close the demonstration

**Say:**

> Authorization and safety are separate controls. Authorization asks whether
> this trusted user may perform this action on this resource. The mutation hook
> asks whether an authorized state change is safe under current conditions.
> Both checks belong in harness code at the execution boundary.
>
> The model proposes actions and explains results. It does not authenticate
> itself, grant roles, decide its own permissions, or bypass a denial. That is
> the core lesson: tool availability creates capability, but the harness owns
> authority.
>
> The remaining scenarios demonstrate both sides of the policy. An incident
> commander can perform an authorized safe rollback, an unassigned support
> engineer cannot read another engineer's incident, an administrator can
> reassign it, and an authorized but unsafe resolution is still blocked by the
> safety hook.

**Optional follow-up command:**

```bash
python3 main.py compare --scenario all
```

This runs basic first and permissions second for all eight labeled scenarios,
then combines their observed outcomes in one final comparison table.
