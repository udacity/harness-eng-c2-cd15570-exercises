# Lifecycle Boundary Contract

This contract specifies what may happen at each production lifecycle boundary.
It is both a design aid and a review checklist.

## Ordered path

```text
session configuration
        |
        v
pre_llm_call: record selected skill delivery
        |
        v
model proposes tool(arguments)
        |
        v
pre_tool_call
  1. permission decision from trusted identity
  2. equivalent-call limit
  3. mutation safety when applicable
        |
        +---- deny/block ----> structured non-execution result
        |
        v
registered handler executes
        |
        v
post_tool_call: parse result, record it, update evidence freshness
        |
        v
model continues or attempts to finish
        |
        v
pre_verify: state + trace oracle
        |
        +---- incomplete ----> bounded corrective nudge
        |
        v
completion event + final response
```

## Boundary invariants

### Before the model

- The runtime, not arbitrary prompt text, selects qualified plugin skills.
- A registered skill and a preloaded skill are different facts.
- Recording should happen once per session even if the callback runs before
  multiple model calls.

### Before every tool

- Identity comes from trusted run context, never model-supplied arguments.
- Unknown tools, identities, roles, or resources deny by default.
- Permission executes first.
- A denial returns structured `executed: false` evidence immediately.
- The repeated-call hook fingerprints canonical tool name and arguments.
- The sixth equivalent call is blocked when five repeats are permitted.
- Mutation safety requires fresh health evidence.
- Rollback targets must exist and be marked last-known-good.
- A block returns structured `executed: false` evidence immediately.

### During tool execution

- Only registered handlers execute.
- The handler is the only stage that may produce `executed: true`.
- Domain state is saved after execution.
- Input errors produce a structured tool error rather than a fabricated
  successful result.

### After tool execution

- The callback observes the authoritative handler result.
- A successful health read marks evidence fresh.
- A successful mutation invalidates that freshness.
- The ordered trace records the tool, arguments, and parsed result.
- Denied and blocked calls never appear as successful `tool_result` events.

### Before completion

- The completion oracle is scenario-specific.
- An execute outcome requires both target state and mutation evidence.
- A deny outcome requires unchanged state and the matching permission denial.
- A block outcome requires unchanged state and the matching safety block.
- Missing evidence produces `continue`, not a false success.
- Runtime bounds constrain repeated completion nudges and total turns.

## Short-circuit table

| Decision | Next stage | Skipped stages | Required trace fact |
| --- | --- | --- | --- |
| Permission deny | Structured result to model | Repeat, safety, handler, post-tool | `permission_decision: deny` |
| Repeat block | Structured result to model | Safety, handler, post-tool | `hook_decision: repeated_call, allowed=false` |
| Safety block | Structured result to model | Handler, post-tool | `hook_decision: mutation_safety, allowed=false` |
| All allow | Handler | None | Allow decisions, then `tool_result` |
| Completion fail | Continue model lifecycle | Final acceptance | `completion_verification, allowed=false` |
| Completion pass | Accept finalization | Further turns | `completion` |

## Failure semantics

Use precise language:

- **Proposed:** the model requested the call.
- **Denied:** authorization rejected it.
- **Blocked:** a deterministic hook rejected an authorized or otherwise
  admitted call.
- **Failed:** a handler ran but returned an error.
- **Executed:** the handler ran; this does not by itself mean the business task
  completed.
- **Completed:** the scenario oracle accepted state and evidence.

“Did not change state” cannot identify which of deny, block, handler failure,
or no proposal occurred. The trace must identify the cause.
