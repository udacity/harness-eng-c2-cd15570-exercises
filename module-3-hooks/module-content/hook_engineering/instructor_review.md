# Instructor Review Packet

## Review status

This package is a complete first draft for technical, instructional, security,
and production review. It is not a finished slide deck or recorded lesson.

## Decisions required before recording

### 1. Determinism language

- [ ] Approve: “For the same validated inputs, trusted state, policy, and code,
  the hook returns the same decision.”
- [ ] Reject any claim that hooks make the entire agent loop deterministic.
- [ ] Confirm hidden inputs—time, network, randomness, environment, mutable
  globals—are identified.
- [ ] Confirm deterministic is never used as a synonym for correct or safe.

### 2. Antidote terminology

- [ ] Approve antidote as course terminology for a check targeting a known
  failure.
- [ ] Preserve the design sequence from failure to invariant, boundary, trusted
  input, predicate, evidence, tests, and residual risk.
- [ ] Confirm every antidote maps to one repository example.
- [ ] Avoid language implying every subjective or unknown failure has a
  deterministic antidote.

### 3. Lifecycle and responsibility

- [ ] Model tool calls are proposals until execution evidence exists.
- [ ] The hook runs after parsing/trusted-state resolution and before dispatch.
- [ ] Permission and validity remain separate decisions.
- [ ] Block results return to the model without calling the business tool.
- [ ] Post-response evaluation is not described as mutation prevention.
- [ ] The model does not choose whether a mandatory hook runs.

### 4. Check design

- [ ] Exact argument shapes and trusted identifiers fail closed.
- [ ] All applicable checks run and findings aggregate.
- [ ] Pass, fail, error, and not-applicable semantics are clear.
- [ ] Demo Boolean “pass” for non-applicable checks is disclosed.
- [ ] Exact threshold and `Decimal` semantics match the exercise.
- [ ] Special decimal values, Booleans, and fractions of a cent are rejected.

### 5. Reliable-loop behavior

- [ ] Replay protection is not overstated beyond its storage scope.
- [ ] Canonical signatures are explained.
- [ ] Successful mutation invalidates old health evidence.
- [ ] Retry limits never waive policy or manufacture success.
- [ ] Hook allow is not conflated with tool success.
- [ ] Tool success is not conflated with desired business outcome.

### 6. Atomicity and concurrency

- [ ] The in-memory demo is distinguished from shared production state.
- [ ] TOCTOU risk is explained without claiming every system is vulnerable.
- [ ] Transactions, locks, expected versions, compare-and-swap, or conditional
  APIs are presented as architecture-dependent solutions.
- [ ] Tests include stale expected-state behavior.

### 7. Testing and measurement

- [ ] Pure predicate and dispatcher wiring tests are separate.
- [ ] Block tests assert the tool call count is zero.
- [ ] Allow tests assert one execution and expected state change.
- [ ] Bypass, malformed, replay, state-machine, and boundary tests are covered.
- [ ] A hook that did not run is labeled “not run,” never pass.
- [ ] Basic-mode rules are “not checked,” never zero failures.
- [ ] Sample metrics carry the illustrative watermark.

## Technical accuracy checklist

- [ ] `MUTATION_TOOLS` contains only rollback and status update.
- [ ] All five incident checks match `demo/hooks.py`.
- [ ] `before_tool_call` blocks unsupported targets, malformed arguments, and
  incident-ID mismatches.
- [ ] The hook executes only in `mode == "hooks"`.
- [ ] A blocked event returns before mutation dispatch.
- [ ] Successful mutation signatures are recorded after execution.
- [ ] Successful mutation resets `health_checked` to false.
- [ ] The model loop sets `parallel_tool_calls=False` and caps cycles at 20.
- [ ] The independent evaluator runs after serving and cannot undo mutations.
- [ ] Module 3 displays but does not enforce the authenticated role.
- [ ] Expense thresholds use `>` exactly as stated.
- [ ] `Decimal(str(value))`, finiteness, and cent precision are all addressed.

## Storyboard review checklist

- [ ] Dotted arrows mean model influence/proposal.
- [ ] Solid gates mean harness control.
- [ ] Proposal cards retain “not executed” until tool evidence.
- [ ] Block animations never show state mutation.
- [ ] Non-applicable and not-run states are visually distinct from pass.
- [ ] Threshold visuals use exact cents.
- [ ] TOCTOU visual retains state-version labels throughout.
- [ ] Charts include counts, denominators, versions, and provenance.
- [ ] Code is readable at 1080p and contains no secrets.
- [ ] Alt text is transferred into final assets.

## Suggested live-demo checkpoints

### Unprotected mutation tool

Ask:

> Where in this function does it decide whether the target is safe?

Expected discussion: nowhere; the function applies the requested mutation, so
the harness boundary must decide first.

### Hook decision

Ask:

> Which values come from the model, and which come from trusted application
> state?

Expected discussion: proposed tool arguments come from the call; incident,
deployment history, freshness, and prior signatures are harness-owned.

### Unsafe comparison

Ask:

> What exact evidence proves the unsafe call did not execute?

Expected discussion: hook block, `MUTATION TOOL: NOT EXECUTED`, unchanged state,
and zero mutation execution event.

### Valid rollback

Ask:

> Why is an allow result necessary but not proof of recovery?

Expected discussion: the target and preconditions passed; execution and
post-action health require separate evidence.

### Expense threshold

Ask:

> Which operator implements “over $500,” and what adjacent tests prove it?

Expected discussion: `>`; $500.00 passes without approval and $500.01 fails.

## Demonstration contingencies

If the model never requests a protected mutation:

> No protected proposal reached the boundary, so the hook did not run. This run
> does not demonstrate an allow or block decision.

If the model repeats an invalid proposal:

> Every proposal is evaluated again. Repetition does not weaken the invariant.

If basic mode avoids the unsafe request:

> The model made a safe choice in this run. Basic mode still has no execution
> guarantee if an invalid proposal occurs.

If the hook allows a valid rollback:

> The gate is selective, not a blanket tool ban. The allow proves the declared
> preconditions passed; it does not prove the mutation succeeded or recovered
> the service.

If the evaluator fails after a mutation:

> The evaluator affects reporting or revision. It cannot undo a completed
> action, which is why mutation policy runs before execution.

## Production checklist

- [ ] Resolve every unchecked decision above.
- [ ] Recheck official OpenAI function-calling documentation.
- [ ] Run the deterministic expense-policy tests.
- [ ] Capture incident allow and block paths with model/date metadata.
- [ ] Replace illustrative terminal visuals with captured evidence.
- [ ] Review every public route to protected tools.
- [ ] Verify concurrency/atomicity claims with the target architecture.
- [ ] Perform security and accessibility review.
- [ ] Time a complete read at natural pace; keep total between 25 and 35
  minutes.
- [ ] Record only after technical and course-alignment approval.

## Recommended acceptance criteria

The package is ready for slide production when:

- all five objectives have matching narration and storyboard coverage;
- hook determinism is narrow, accurate, and consistently qualified;
- every antidote maps failure, invariant, predicate, tests, and residual risk;
- examples match repository behavior and exercise thresholds;
- the non-execution guarantee is demonstrated with integration evidence;
- atomicity and authorization limits are explicit; and
- no unresolved technical or security item remains.
