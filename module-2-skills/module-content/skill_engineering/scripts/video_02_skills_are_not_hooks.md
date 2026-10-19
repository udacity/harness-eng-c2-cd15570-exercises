# Video 2 — Skills Are Not Hooks

**Target duration:** 6 minutes 15 seconds  
**Learning objective:** Distinguish model-facing guidance from lifecycle
enforcement and assign each requirement to the correct harness component.

## Instructor narration

### [Slide 1] Same policy, different guarantees — 0:00–0:55

Suppose the safe-remediation skill says: before a production rollback, check a
fresh health snapshot, verify the proposed target is last-known-good, obtain
authorization, and define post-action verification.

That is strong operational guidance. But what happens if the model overlooks
one step and calls `rollback_deployment` with the wrong target?

If the only protection is skill text, the application may still execute the
request. The instruction influenced the model; it did not control the
execution boundary.

That is the difference between a skill and a hook.

### [Slide 2] A skill changes model context — 0:55–1:50

A skill is selected because its guidance appears relevant to the task. The
harness loads the text, and the model uses that context to decide what to say
or propose.

Selection and adherence are inferential. The model may omit a relevant skill,
load an irrelevant one, misunderstand a rule, or follow two conflicting skills
inconsistently.

Skills are excellent for procedures that require judgment: how to triage an
incident, how to phrase an update, which diagnostic evidence usually matters,
or how to structure a campaign. They make behavior more informed and reusable.

But the phrase “the skill says never” does not create a hard guarantee.

### [Slide 3] A hook changes the harness path — 1:50–2:50

A hook is application code registered at a lifecycle event. A before-tool hook
runs after the model proposes a call and before the harness dispatches it. It
can inspect validated arguments and trusted state, then allow, block, modify,
or record the operation.

The model does not need to remember to request a mandatory hook. The harness
invokes it because execution reached that boundary.

In Module 3, the rollback hook checks the target against trusted deployment
history. If the target is not last-known-good, the hook returns a block result
and the mutation tool does not run. For the same trusted input, ordinary code
can produce the same decision every time.

Hooks are only as reliable as their wiring and implementation, so tests must
prove that every sensitive path passes through them.

### [Slide 4] Use both layers — 2:50–3:45

The right architecture is usually not skills versus hooks. It is skills plus
hooks, with separate responsibilities.

The remediation skill helps the model propose one controlled action, explain
why evidence matters, and plan verification. The hook protects the application
if the proposal violates an exact invariant.

When a call is blocked, the result returns to the model. The skill helps the
model explain what evidence is missing and choose a safer next step. The hook
provides the enforcement evidence.

Guidance improves proposals. Enforcement constrains effects.

### [Slide 5] Do not confuse neighboring components — 3:45–5:00

A tool is also different. A tool exposes data or an action. `load_skill` is a
tool that retrieves instructions; `get_service_health` retrieves current
state; `rollback_deployment` performs a mutation. Tool availability does not
itself decide whether a call is permitted.

A permission policy answers who may act on which resource. A hook can call or
compose with that policy, but the skill must not grant authority.

An evaluator checks whether the completed response satisfies acceptance
criteria. It can detect an inaccurate claim after generation, but a
post-response evaluator cannot undo an unsafe tool execution.

Retrieval supplies changing facts. Those facts should not be frozen in a skill
body. The skill can describe how to interpret them.

Finally, base instructions contain rules every request needs. Routing a
universal safety requirement through an optional skill creates a bypass.

### [Slide 6] A practical placement test — 5:00–5:50

Ask four questions for every requirement.

Is this reusable know-how the model needs for only some tasks? Use a skill.

Must code run whenever a lifecycle event occurs? Use a hook.

Does the requirement depend on authenticated identity, current data, or an
external action? Use permissions, retrieval, or a tool.

Must the finished result be accepted only after a check? Use deterministic or
inferential evaluation.

One business rule may appear in several layers, but each representation has a
different job. The skill explains. The hook gates. The evaluator verifies the
reported outcome.

### [Slide 7] Boundary statement — 5:50–6:15

Write this statement into the design review:

> No skill grants authority, proves facts, guarantees compliance, or replaces
> a required runtime control.

With that boundary established, we can author skills for what they do well:
delivering focused, reusable task guidance.

## Demonstration cue

Show `demo/skills/safe_remediation/SKILL.md` beside
`module-3-hooks/demo/hooks.py`. Highlight advisory wording in the skill and the
allow/block return path in the hook.

## Transition line

> A hook owns the gate. A skill should now be optimized for discovery,
> comprehension, and correct task use.
