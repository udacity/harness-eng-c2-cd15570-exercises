# Video 3 — Wire Controls to Lifecycle Boundaries

**Target runtime:** 7 minutes  
**Teaching purpose:** Trace exact control order, short-circuit behavior,
evidence freshness, and completion verification.

## Opening

Production correctness depends not only on which controls exist, but where and
in what order they run. The same permission policy placed after tool execution
would be an audit log, not prevention. A completion check based on final prose
would be a style judgment, not a state oracle.

Open `register()` in `demo/plugin_impl.py`.

## Before the model

The plugin registers two skills: `incident_triage` and `safe_remediation`.
Registration makes them available by qualified name. The CLI selects them with
`--skills`.

At `pre_llm_call`, `before_model()` records `skills_preloaded` once. This is an
evidence callback; Hermes owns actual delivery to the model lifecycle.

Keep three facts separate:

1. a skill file exists;
2. the plugin registered the skill; and
3. the session selected and preloaded it.

Only the third means the procedure can influence model decision-making in this
run.

## Before every tool

The most security-sensitive method is `before_tool()` at `pre_tool_call`.

First, the plugin calls the permission policy with the trusted user, tool name,
arguments, and current incident. The model does not choose its own role. An
unknown tool, invalid identity, unknown incident, or missing permission denies
by default.

If permission denies, the callback immediately returns `action: block` with a
structured `permission_denied` result and `executed: false`. The model can
observe the result and continue, but the repeat hook, safety hook, and handler
do not run for that proposal.

Second, an authorized proposal reaches the repeated-call hook. It canonicalizes
the tool and arguments, hashes that representation, and counts equivalent
calls. Calls one through five are permitted. The sixth is blocked. Sorting JSON
keys means superficial argument ordering does not evade the limit.

Third, a mutation reaches the safety hook. A rollback requires fresh service
health. Its target must appear in deployment history and must be marked
last-known-good. An attempt to mark the incident resolved requires healthy
service state and confirmed recovery.

If safety blocks, the handler does not run. If all applicable checks allow,
returning `None` tells Hermes that it may dispatch the registered handler.

```text
proposal
  -> trusted permission
  -> equivalent-call limit
  -> mutation safety
  -> registered handler
```

Order matters. Authorization comes first so an unauthorized subject cannot use
safety behavior as an alternate access path. Deterministic safety comes before
the side effect because detection afterward cannot prevent damage.

## During and after execution

The registered handler calls the incident tool, marks a successful result
`executed: true`, and saves domain state. Invalid inputs return a structured
tool error with `executed: false`.

At `post_tool_call`, `after_tool()` parses the authoritative handler result and
records `tool_result`. A successful health read marks health evidence fresh. A
successful mutation invalidates it, because system state changed after the
observation.

This is a small but important production pattern: evidence has a lifecycle.
Reading health once does not create a permanent license for future mutations.

Denied and blocked proposals do not produce a successful handler result. The
trace must never transform non-execution into execution merely because the
model received a structured response.

## Before completion

When the model attempts to finish, Hermes calls `pre_verify`. The plugin's
`before_completion()` asks `CompletionHook` to compare authoritative incident
state with ordered trace events.

For `safe-rollback`, final deployment must be `checkout-v41` and rollback state
must show that the mutation occurred.

For `unauthorized-rollback`, deployment must remain `checkout-v42`, and the
trace must contain the rollback permission denial.

For `unsafe-rollback`, deployment must remain `checkout-v42`, and the trace
must contain a failed hook decision for the rollback.

Unchanged state alone is insufficient. It could mean the model never proposed
the action, the handler failed, or the expected boundary was never exercised.

If the check passes, the plugin records `completion`. If it fails, the callback
returns `action: continue` with a corrective nudge. Hermes then continues the
model lifecycle. The profile's maximum turns and verification nudges bound that
recovery.

## Precise outcome vocabulary

Use these terms consistently:

- proposed: the model requested a tool;
- denied: permission rejected authority;
- blocked: a deterministic hook rejected an admitted proposal;
- failed: the handler ran but returned an error;
- executed: the handler actually ran;
- completed: the scenario oracle accepted state and trace evidence.

A completed unauthorized scenario is not contradictory. The business task for
that scenario is to demonstrate the denial while preserving state.

## Closing

Production integration is executable ordering. Skills arrive before decisions.
Authorization comes before safety. Safety comes before side effects. Result
observation comes after actual execution. Completion uses state and trace before
final acceptance.

Next, we will run the three scenarios and use those boundaries to prove both
operational usefulness and prevention.

## On-screen repository anchors

- `demo/plugin_impl.py`: all four lifecycle callbacks
- `demo/components/permissions.py`: trusted default-deny policy
- `demo/components/hooks.py`: repeat, safety, and completion hooks
- `demo/incident_tools.py`: handler dispatch and domain mutation
