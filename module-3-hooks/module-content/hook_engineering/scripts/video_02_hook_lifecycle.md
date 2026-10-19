# Video 2 — Place Hooks in the Lifecycle

**Target duration:** 6 minutes 15 seconds  
**Learning objective:** Place deterministic controls at the correct event and
preserve the separation between proposal, authorization, validation, execution,
and evaluation.

## Instructor narration

### [Slide 1] A tool call is a proposal — 0:00–0:50

When the model emits `rollback_deployment`, nothing in production has changed
yet. The response contains a tool name, arguments, and call identifier. The
application decides what happens next.

That distinction is essential. If a log labels the model response “rollback
completed,” it has erased the only place where policy can intervene.

Use precise verbs: requested, parsed, authorized, allowed, executed, and
verified. Each needs different evidence.

### [Slide 2] The before-tool path — 0:50–1:50

The safe path begins by parsing arguments and validating their shape. The
harness resolves the active incident and other trusted state. In a complete
system it checks whether the authenticated subject may perform this action.
Then the before-tool safety hook runs its antidotes.

If all required checks pass, the dispatcher calls the business tool. If any
check fails or errors, the dispatcher returns a structured block result and
does not call the tool.

The placement is the guarantee. A correct predicate that runs after dispatch is
only a detector.

### [Slide 3] Why the tool remains policy-light — 1:50–2:40

The Module 3 mutation functions directly change incident state. They do not
contain rollback-target or resolution policy. This makes the comparison visible
and lets the same tool serve basic and protected modes.

In production, tools still validate their own low-level contract and may use
database constraints. But cross-cutting harness policy belongs at a shared
boundary where it can be versioned, observed, and reused.

Do not accidentally run policy twice with different rules. Define one source
of truth and treat deeper database constraints as defense in depth.

### [Slide 4] Block is feedback, not a crash — 2:40–3:30

When a hook blocks, the tool remains uncalled. The harness creates a
`function_call_output` correlated with the original call ID. Its payload says
the action was blocked and lists violations.

The next model cycle can explain the decision, request fresh evidence, or
propose a different allowed action. The process continues under normal loop and
budget limits.

Returning structured evidence matters. A generic exception may prompt blind
retries. A named violation gives the model and operator a concrete recovery
path.

### [Slide 5] Other lifecycle hooks — 3:30–4:25

Before-tool is one lifecycle event.

A pre-model hook may normalize allowed context or enforce a budget. An
after-tool hook may validate or redact returned data and invalidate stale
evidence. A before-completion hook may require tests or terminal evidence. A
cycle hook may detect repetition or enforce a maximum.

These hooks are not interchangeable. A completion hook can prevent the harness
from announcing success, but it cannot undo an already executed mutation. An
after-tool hook can detect a bad result, but prevention must happen before or
inside an atomic operation.

### [Slide 6] Ordering distinct decisions — 4:25–5:20

In a cumulative harness, order matters.

First parse the call. Then resolve trusted identity and state. Permission asks
whether this subject may perform this action on this resource. The safety hook
asks whether the specific proposed action is valid now. Only then does the tool
execute. Postconditions and final evaluation come afterward.

An authorized user can still propose an invalid rollback. A valid rollback can
still be unauthorized for the caller. Both decisions must pass, and neither is
delegated to the model.

Module 3 displays the user but intentionally postpones permission enforcement
to Module 4.

### [Slide 7] Cover every route — 5:20–5:55

A hook protects only traffic that passes through it. Inventory direct tool
calls, alternate API endpoints, queues, scheduled jobs, administrative paths,
and retry workers. Centralize dispatch or enforce the invariant again at the
transactional data boundary.

Tests should attempt bypasses. A unit test of the predicate cannot prove the
application always invokes it.

### [Slide 8] Transition — 5:55–6:15

We now know where hooks run. The next question is what they run.

The course calls each exact defense against a known failure an antidote. We
will turn concrete failures into invariants and executable checks.

## Demonstration cue

Trace the `mode == "hooks"` branch in `demo/agent.py` from parsed call through
`before_tool_call()`, block/allow, dispatch, and correlated output.

## Transition line

> A hook supplies the control point. An antidote supplies the rule.
