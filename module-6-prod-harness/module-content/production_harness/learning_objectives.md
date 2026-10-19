# Learning Objectives

By the end of Module 6, students will be able to:

## 1. Define production ownership

- Separate generic agent-runtime responsibilities from domain-plugin
  responsibilities.
- Explain why a launcher or adapter must not quietly duplicate the framework's
  model loop.
- Identify an owner for tools, skills, authorization, safety invariants,
  completion criteria, state, and usage evidence.

**Evidence of mastery:** Given an implementation, the student labels each
responsibility and identifies duplicated or missing ownership.

## 2. Package and activate a plugin

- Distinguish manifest declaration, profile activation, and per-session
  capability selection.
- Register tool handlers, qualified skills, and lifecycle hooks through the
  runtime's supported extension interface.
- Interpret plugin validation as structural compatibility evidence rather than
  end-to-end business proof.
- Use a dry run to inspect a resolved command without claiming that a scenario
  executed.

**Evidence of mastery:** The student can explain what a successful validator
result proves, what it does not prove, and which runtime test supplies the
missing evidence.

## 3. Wire controls to exact lifecycle boundaries

- Load scoped skill context before model decision-making.
- Apply trusted authorization before repeated-call and mutation-safety checks.
- Observe authoritative tool results after execution.
- Verify completion before accepting the final response.
- Preserve structured non-execution results for denied and blocked calls.

**Evidence of mastery:** The student constructs the sequence `permission ->
repetition -> safety -> execution -> observation -> completion` and predicts
which stages are skipped for each failure path.

## 4. Keep permissions and safety distinct

- Evaluate authorization from trusted subject, action, and resource inputs.
- Evaluate safety from current domain state and proposed mutation inputs.
- Explain why an action may be safe but unauthorized, or authorized but unsafe.
- Preserve default-deny and fail-closed behavior when inputs are unknown or
  malformed.

**Evidence of mastery:** The student correctly classifies the unauthorized and
unsafe rollback scenarios without calling one boundary the other.

## 5. Prove useful operation with controlled scenarios

- Use a positive control to show that legitimate work can pass.
- Reset authoritative state before every scenario.
- Use paired scenarios to prove execute, deny, and block outcomes.
- Avoid treating “nothing changed” as sufficient evidence of the reason.

**Evidence of mastery:** The student verifies both final deployment state and
the exact permission, hook, and tool events required by each oracle.

## 6. Verify completion from evidence

- Distinguish process success, model finalization, tool execution, and business
  completion.
- Define scenario-specific completion criteria from authoritative state and
  trace events.
- Use bounded completion nudges to recover missing work without creating an
  unbounded retry loop.

**Evidence of mastery:** The student rejects a fluent success claim when state
or trace evidence is absent and writes an actionable corrective nudge.

## 7. Operate and test the integrated harness

- Interpret state, ordered JSONL trace, usage, and derived summary artifacts.
- Test registrations and policy paths deterministically without model calls.
- Reserve live-model runs for integration behavior that deterministic tests
  cannot establish.
- Preserve fresh state, isolated profiles, scoped capabilities, and bounded
  execution.

**Evidence of mastery:** The student designs a layered test matrix and can map
each production claim to its supporting artifact or test.

## 8. Compare integration approaches responsibly

- Compare a hand-built loop and a framework integration by responsibility,
  lifecycle clarity, evidence, and maintenance risk.
- Require behavioral parity before discussing integration effort.
- Avoid conclusions based only on generated code style, small timing
  differences, different providers, or raw line count.

**Evidence of mastery:** The student recommends an approach for a stated
operational context and names the tradeoff and evidence behind the choice.

## 9. State production limitations

- Distinguish this local isolated demo from deployment infrastructure, secret
  management, distributed reliability, and organization-wide authorization.
- Identify the additional release, monitoring, incident, and rollback plans a
  real service would require.
- Treat observed model behavior and captured traces as scoped evidence, not a
  universal guarantee.

**Evidence of mastery:** The student names at least three untested production
  risks and proposes the next validation step for each.
