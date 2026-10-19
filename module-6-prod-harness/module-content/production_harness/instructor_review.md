# Instructor Review Packet

## Review status

This packet is ready for technical, instructional-design, operations, security,
and visual review. Resolve every blocking item before recording.

## Decisions requiring approval

### 1. Central thesis

Approve this exact statement:

> A production harness assigns generic lifecycle mechanics to one runtime,
> connects domain controls at explicit boundaries, allows legitimate work,
> prevents unauthorized or unsafe work, and proves every outcome with
> authoritative evidence.

### 2. Runtime ownership

Approve the division in this repository:

- Hermes owns model lifecycle, continuation, sessions, hook dispatch,
  completion nudges, bounds, and usage accounting.
- The plugin owns incident tools, skills, trusted permissions, deterministic
  invariants, completion criteria, and domain trace semantics.
- `run_demo.py` is isolated launch support, not a second agent loop.

### 3. Scenario order

Approve introducing all three use cases before plugin validation or dry run.
The safe case must be described as the positive control.

### 4. Proof vocabulary

Approve the strict distinction among declared, activated, selected, validated,
proposed, denied, blocked, executed, failed, and completed.

### 5. Exercise conclusion

Approve a responsibility-based comparison. Reject framework rankings based
only on raw line count, generated-client style, captured cycle count, or the
small observed behavioral-test duration difference.

## Technical accuracy checklist

- [ ] Every scenario starts from degraded `checkout-v42` and fresh state.
- [ ] `safe-rollback` uses Morgan and last-known-good `checkout-v41`.
- [ ] `unauthorized-rollback` uses Sam and safe `checkout-v41`.
- [ ] `unsafe-rollback` uses Morgan and non-LKG `checkout-v40`.
- [ ] Safe outcome executes and ends on `checkout-v41`.
- [ ] Denied and blocked outcomes do not execute and remain on `checkout-v42`.
- [ ] The plugin registers six tools, two skills, and four hook events.
- [ ] The profile enables the plugin and exposes its CLI toolset.
- [ ] Project skill discovery and coding context are off in the demo profile.
- [ ] Maximum turns are 20 and maximum verification nudges are 4.
- [ ] Permission precedes repeated-call and mutation-safety checks.
- [ ] The repeated-call hook permits five equivalent calls and blocks the sixth.
- [ ] Mutations require fresh service-health evidence.
- [ ] Successful mutations invalidate fresh-health evidence.
- [ ] Completion checks authoritative state and matching boundary evidence.
- [ ] Reviewers understand that the demo's unsafe completion oracle accepts any
      failed rollback hook; the hardened teaching example requires the exact
      `mutation_safety` block.
- [ ] A failed completion check returns a bounded continuation request.

## Package and command checklist

- [ ] Manifest declaration is not called activation.
- [ ] Profile activation is not called per-session skill selection.
- [ ] Validator success is not called workflow success.
- [ ] Validation capability handlers are not presented as real incident tools.
- [ ] `safe-rollback --dry-run` is introduced only after the scenario.
- [ ] Dry run is described as command preview only.
- [ ] The displayed command includes workspace, route, usage, toolset, and
      qualified skills.
- [ ] The isolated profile does not expose unrelated plugins or skills.
- [ ] Credential values and personal profile paths are not displayed.

## Evidence checklist

- [ ] `incident.json` is described as authoritative final domain state.
- [ ] `run.jsonl` is described as ordered lifecycle evidence.
- [ ] `usage.json` is described as Hermes runtime usage evidence.
- [ ] `run-result.json` is labeled a derived compact summary.
- [ ] Return code zero is not called business completion.
- [ ] Final model prose is not used as execution truth.
- [ ] Denied and blocked calls preserve `executed: false`.
- [ ] Unchanged state is paired with the exact denial or block cause.
- [ ] Registered and preloaded skills are separate trace facts.
- [ ] Any disagreement among artifacts is investigated, not averaged away.

## Test-strategy checklist

- [ ] Plugin validation runs on the recording environment.
- [ ] Deterministic demo tests make no provider calls.
- [ ] Registration, permissions, safety, repeat, completion, trace, and command
      construction have test coverage.
- [ ] Allowed and prevented mutation paths are both tested.
- [ ] Unknown tools, identities, and resources fail closed.
- [ ] All three live scenarios are rerun before behavior claims are recorded.
- [ ] Model-dependent extra calls are described as observations.
- [ ] Failed or incomplete live runs are not edited into apparent successes.

## Exercise-alignment checklist

- [ ] Both harnesses begin with identical incomplete client templates.
- [ ] Both retrieve the current fictional contract from local `/api-docs`.
- [ ] Public web access remains denied.
- [ ] File access is scoped to each assigned generated-client workspace.
- [ ] Permission runs before repeat control and tool execution.
- [ ] Syntax checks run after writes.
- [ ] Completion requires the fixed behavioral test.
- [ ] Each generated client passes the same test before comparison.
- [ ] The Python loop's extra lifecycle ownership is explained accurately.
- [ ] Hermes adapter work is not described as “configuration only.”
- [ ] The saved comparison is labeled captured evidence, not a benchmark.

## Instructional-design checklist

- [ ] Video 1 introduces use cases and ownership before implementation.
- [ ] Video 2 separates declaration, activation, validation, selection, and run.
- [ ] Video 3 traces ordering and short circuits.
- [ ] Video 4 proves usefulness, authority, and safety with four artifacts.
- [ ] Video 5 layers tests and transfers the pattern to the exercise.
- [ ] Students see why a positive control is required.
- [ ] Students see safe-but-unauthorized and authorized-but-unsafe cases.
- [ ] Students explain why a completed denial case did not execute a rollback.
- [ ] Production extensions are clearly outside the local demo proof.

## Suggested recording sequence

1. Open `data.py`; introduce the three scenarios and fresh initial state.
2. Draw the Hermes-versus-plugin ownership boundary.
3. Open `plugin.yaml`, the entry point, and `.hermes/config.yaml`.
4. Run plugin validation and state exactly what it proves.
5. Run `safe-rollback --dry-run` and explain every selected capability.
6. Open `register()` and trace all four callbacks.
7. Run or reveal safe rollback; reconcile state, trace, usage, and summary.
8. Repeat for unauthorized rollback and unsafe rollback.
9. Run deterministic tests and map representative tests to claims.
10. Open both exercise integrations and compare ownership after parity.
11. End with scope, production extensions, and the final principle.

## Discussion prompts

1. Which lifecycle responsibilities should your framework own?
2. Which domain decisions cannot be delegated to the model or framework?
3. What is your positive control for useful production work?
4. Which identity inputs are trusted, and how are they bound to a run?
5. What evidence becomes stale after a mutation?
6. What state and trace facts define completion?
7. Which failures should continue the model, and which should stop the run?
8. How are retries, calls, turns, and completion nudges bounded?
9. Which artifacts require redaction or restricted retention?
10. What is the release rollback plan for the harness itself?

## Known limitations to say aloud

- The incident, state store, tools, and users are fictional and local.
- A real scenario uses a model, so its path and prose can vary.
- The isolated temporary profile is not a full production sandbox.
- Supported credential copying is not a complete secret-management design.
- JSON files do not provide distributed concurrency or durable storage.
- The local trace is not a complete metrics, alerting, or audit platform.
- Validator security scanning is not a security certification.
- Three scenarios do not cover all incident-response failure modes.
- The current unsafe-scenario completion oracle should be narrowed to the exact
  mutation-safety hook and code before treating it as a production release gate.
- The exercise comparison is not a controlled model/provider benchmark.
- Passing tests does not establish universal reliability or safety.

## Final sign-off

| Reviewer | Focus | Status | Notes |
| --- | --- | --- | --- |
| Module instructor | Learning sequence | Pending | |
| Repository maintainer | Code and CLI alignment | Pending | |
| Runtime reviewer | Hermes lifecycle accuracy | Pending | |
| Security reviewer | Identity, permission, and safety claims | Pending | |
| Operations reviewer | Evidence, bounds, and limitations | Pending | |
| Instructional designer | Timing and cognitive load | Pending | |
| Visual producer | Accessibility and redaction | Pending | |
