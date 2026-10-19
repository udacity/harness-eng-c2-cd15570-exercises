# Skills Versus Hooks: Decision Reference

## Short rule

> Put reusable know-how in a skill. Put non-negotiable lifecycle enforcement in
> a hook.

## Detailed comparison

| Dimension | Skill | Hook |
| --- | --- | --- |
| Primary purpose | Supply specialized instructions, procedures, examples, or context | Inspect or control a harness lifecycle event |
| Owner | Skill author plus catalog/loader | Harness/application code |
| Trigger | Task match, router, user selection, or model request | A wired event such as before tool execution |
| Model involvement | Usually chooses or receives it; may follow imperfectly | Does not decide whether a mandatory hook runs |
| Typical implementation | `SKILL.md` plus optional resources | Code registered at a named lifecycle boundary |
| Output | Additional model context | Allow, block, transform, annotate, log, or raise |
| Determinism | Model adherence and selection are probabilistic | Code path can be deterministic for the same trusted input |
| Security role | Advisory unless paired with enforcement | Can enforce an invariant if correctly wired and fail-closed |
| Failure example | Relevant skill omitted or instruction ignored | Hook absent, bypassed, misordered, or incorrectly implemented |
| Test focus | Routing and end-task behavior | Boundary coverage and exact allow/block behavior |

## One rule implemented at two layers

Requirement: only roll back to a verified last-known-good deployment.

### Skill contribution

```text
Before recommending rollback, review deployment history, confirm the proposed
target is marked last-known-good, obtain authorization, and plan verification.
```

This helps the model propose a cautious plan and explain the reasoning. The
model may still omit the check, misread the evidence, or request an unsafe
target.

### Hook contribution

```python
def before_tool_call(name, args, trusted_state):
    if name == "rollback_deployment":
        return args["target_version"] in trusted_state.last_known_good
    return True
```

This is schematic. The production hook also needs argument validation,
authorization integration, failure evidence, and fail-closed behavior.

### Combined result

The skill produces better proposals and explanations. The hook prevents a
prohibited proposal from becoming an executed action. Neither substitutes for
the other.

## Classification exercises

| Requirement | Place it in | Why |
| --- | --- | --- |
| “Use a calm stakeholder tone.” | Skill | Domain/style guidance for generation. |
| “Never execute a duplicate refund.” | Before-tool hook | Exact pre-execution invariant. |
| “Read the current order status.” | Retrieval tool | Volatile authoritative data. |
| “Only finance managers may approve.” | Permission policy | Identity/resource authorization. |
| “Send the refund.” | Business tool | External action. |
| “The answer must contain the incident ID.” | Deterministic evaluator/check | Verifiable final-output condition. |
| “Always answer in JSON for every task.” | Base instruction or structured output | Universal, not task-selective. |

## Warning signs that a skill is being misused

- “The skill guarantees the model will comply.”
- “Loading the skill authorizes the action.”
- “The skill checks the current database state” when no retrieval occurs.
- “The model will remember to run the safety check.”
- “The skill replaces validation because its instructions are detailed.”
- “The model-selected skill decides which mandatory hook runs.”
