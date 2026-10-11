# Module 3 Demo: Six-Minute Instructor Script

## Before the demonstration

Confirm that the dependencies are installed and that `.env` contains a current
Vocareum `OPENAI_API_KEY`. Start in `module-3-hooks/demo`.

Keep these files open in the editor:

1. `scenarios/unsafe_remediation.json`
2. `tools.py`
3. `hooks.py`
4. `agent.py`
5. `main.py`

Use `unsafe_remediation` for the recorded demonstration because it makes both
unsafe state changes visible: rollback to `checkout-v40`, which is not marked
last-known-good, and a request to mark a degraded incident `RESOLVED`. Live
models can vary the number and order of retrieval, skill, and mutation calls.
Describe the observed run rather than promising exact cycle or request counts.

## 0:00–0:55 — Define a mutation

**Show:** `scenarios/unsafe_remediation.json`.

**Say:**

> This demo continues incident `INC-2048`. Production `checkout-api` is
> degraded with an 18 percent error rate. `checkout-v42` is active,
> `checkout-v41` is the last-known-good deployment, and recovery is not
> confirmed.
>
> In this module, a mutation is simply a tool call that changes stored incident
> state. `rollback_deployment` changes the active deployment, and
> `update_incident_status` changes the incident status. Health, logs,
> deployment history, and skill loading are read-only calls.
>
> The operator asks for rollback to `checkout-v40` and then asks to mark the
> incident resolved. Those are intentionally unsafe proposals given the trusted
> state.

## 0:55–1:50 — Show the unprotected tools

**Show:** `rollback_deployment` and `update_incident_status` in `tools.py`.

**Say:**

> These mutation tools perform exactly the requested state change. The rollback
> function replaces the current deployment, and the status function writes the
> requested status. Neither function contains safety policy.
>
> That separation is deliberate. In basic mode, a model request reaches these
> tools directly. Instructions and skills may tell the model to be cautious,
> but they cannot guarantee that an unsafe tool request will never occur. Once
> the tool executes, a later evaluator can report the mistake but cannot undo
> the side effect.

**Point out:**

- A model tool call is initially a proposal, not proof of execution.
- The application controls whether the proposed call reaches the tool.
- The same permissive tools are used in both modes.

## 1:50–3:05 — Explain the before-tool hook

**Show:** `before_tool_call` and `validate_mutation` in `hooks.py`.

**Say:**

> Hooks mode inserts deterministic Python checks immediately before a mutation
> tool. The hook verifies fresh health evidence, confirms that a rollback target
> exists and is marked last-known-good, prevents an identical mutation from
> executing twice, and permits `RESOLVED` only when health is `HEALTHY` and
> recovery is confirmed.
>
> Every applicable check contributes to one allow-or-block decision. Malformed
> arguments, an unexpected tool, or an incident-ID mismatch fail closed. These
> checks do not ask the model for another opinion.

**Show:** the `mode == "hooks"` branch in `_tool_result` in `agent.py`.

**Say:**

> This placement is the key. The hook runs after the model proposes arguments
> but before the mutation function executes. An allowed call reaches the same
> tool used by basic mode. A blocked call never reaches that tool; instead, the
> violations return to the model as a function result so the loop can explain
> what happened.

**Summarize the boundary:**

```text
model proposes mutation
          ↓
before_tool_call checks trusted state
          ↓
     ALLOW or BLOCK
          ↓
tool executes, or violations return to the model
```

## 3:05–6:10 — Run and narrate the comparison

**Show:** the terminal in `module-3-hooks/demo`.

**Run:**

```bash
python3 main.py compare --scenario unsafe_remediation
```

### At the scenario display

**Say:**

> Both modes receive the same operator request, initial incident, skill catalog,
> and tool definitions. The only intended difference is whether the
> before-tool hook protects mutation execution.

### During `MODE: BASIC`

For skill-loading and read-only retrieval cycles, identify the call briefly and
press Return. Do not narrate every cycle in detail.

**Say when the first mutation is requested:**

> The model has proposed a state-changing tool. Basic mode prints that hooks are
> disabled, so no invariant is checked. `MUTATION TOOL EXECUTED` confirms that
> the proposal crossed the execution boundary.

At the status mutation, point out the same sequence and press Return.

**Say after the final note and execution summary:**

> Basic mode executed the requested mutations without a safety decision. The
> summary shows the observed final state. In the intended unsafe case, that is
> `checkout-v40` and `RESOLVED`, even though the service remains degraded and
> recovery is unconfirmed.

Briefly acknowledge the independent evaluation result. Emphasize that it runs
after tool execution and therefore cannot prevent an already completed change.

### During `MODE: HOOKS`

Again, move quickly through skill-loading and read-only retrieval cycles by
pressing Return after identifying them.

**Say when rollback to `checkout-v40` is proposed:**

> The same mutation now reaches `before_tool_call`. The target exists in
> deployment history, but it is not marked last-known-good. The failed check
> produces a violation, `HOOK RESULT: BLOCKED`, and `MUTATION TOOL: NOT
> EXECUTED` confirms that incident state was not changed.

Press Return after reviewing the displayed checks.

**Say when `RESOLVED` is proposed:**

> The resolution rule compares the request with trusted health and recovery
> state. The service is still degraded and recovery is unconfirmed, so the hook
> blocks this call before the status tool runs.

Press Return. If the live model repeats a request, say:

> The model repeated a proposal, and the harness evaluated it again. Repetition
> does not bypass the execution boundary; the final table records the observed
> allow and block counts.

After the final note, press Return and briefly describe the independent
evaluation and execution summary.

### At `WHY HOOKS ARE SAFER`

**Say:**

> This table puts the outcomes side by side. `Basic final` is explicitly marked
> unchecked. `Hooks final` shows the state after every mutation proposal passed
> through deterministic checks.
>
> The hook-decision column names what was allowed or blocked. The safety-benefit
> column explains the practical difference: the hook prevents rollback to a
> version not marked last-known-good and keeps the incident open while service
> is degraded.
>
> Hooks are not a blanket ban on tools. The `valid_rollback` scenario allows
> rollback to `checkout-v41` when the required checks pass. Run all scenarios
> after the presentation to see unsafe changes blocked and the valid change
> allowed in one table.

## 6:10–6:45 — Close the demonstration

**Say:**

> The model still decides which tools to request and can explain returned
> violations. The hook owns a different responsibility: it enforces invariants
> at the last safe moment before a side effect.
>
> Skills provide guidance, and evaluators inspect results. A before-tool hook
> prevents an invalid mutation from happening. Module 4 will add authorization,
> deciding not only whether an action is safe for the incident state, but also
> whether the authenticated user is allowed to perform it.

**Optional follow-up command:**

```bash
python3 main.py compare --scenario all
```

