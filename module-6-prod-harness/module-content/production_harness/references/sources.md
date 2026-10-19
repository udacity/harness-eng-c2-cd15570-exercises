# Sources and Research Notes

Reviewed October 18, 2026. Recheck repository behavior and the installed Hermes
version before final recording.

## R1 — Incident production-harness demo

Primary local sources:

- `module-6-prod-harness/demo/README.md`
- `module-6-prod-harness/demo/script.md`
- `module-6-prod-harness/demo/data.py`
- `module-6-prod-harness/demo/run_demo.py`
- `module-6-prod-harness/demo/plugin_impl.py`
- `module-6-prod-harness/demo/incident_tools.py`
- `module-6-prod-harness/demo/components/permissions.py`
- `module-6-prod-harness/demo/components/hooks.py`
- `module-6-prod-harness/demo/components/skills/*/SKILL.md`

**Relevant use:** Authoritative course source for the three scenarios, runtime
ownership boundary, command construction, profile isolation, trusted users,
tool behavior, permission order, safety rules, repeated-call limit, completion
verification, trace events, and four output artifacts.

**Guardrail:** The demo uses a model for real scenario runs. Exact tool order,
extra reads, retries, and final prose may vary. Deterministic code defines the
allowed boundaries and authoritative completion criteria. The current unsafe
completion branch accepts any failed rollback hook; the course's hardened
example narrows that evidence to `mutation_safety`.

## R2 — Plugin package and activation

Primary local sources:

- `module-6-prod-harness/demo/.hermes/plugins/incident-response-demo/plugin.yaml`
- `module-6-prod-harness/demo/.hermes/plugins/incident-response-demo/__init__.py`
- `module-6-prod-harness/demo/.hermes/config.yaml`

**Relevant use:** Authoritative source for plugin identity/version, declared
tools and hooks, entry-point behavior, profile activation, toolset exposure,
skill-discovery setting, coding-context setting, turn limit, and verification-
nudge limit.

**Guardrail:** The plugin validator output depends on the installed Hermes
version. Record the actual output from the recording environment. A validation
pass is structural compatibility evidence, not a scenario result.

## R3 — Deterministic demo tests

Primary local source:

- `module-6-prod-harness/demo/test_demo.py`

**Relevant use:** Supplies model-free verification of registration, manifest
and profile activation, skill-preload evidence, safe execution, permission
denial, hook blocking, completion continuation, trace shape, permission rules,
safety freshness, repeat limits, initial incompleteness, and CLI command flags.

**Guardrail:** Unit and local integration tests do not prove provider
authentication, live model behavior, or compatibility with a future runtime
version.

## R4 — Production-harness exercise

Primary local sources:

- `module-6-prod-harness/exercise-prod-harness-starter/README.md`
- `module-6-prod-harness/exercise-prod-harness-starter/python/loop/configured_agent_loop.py`
- `module-6-prod-harness/exercise-prod-harness-starter/hermes/configured_plugin.py`
- supplied Python and Hermes skills, hooks, permissions, runners, and tests

**Relevant use:** Defines the XYZ API task, the unknown-contract requirement,
the equivalent component sets, the separate generated-client workspaces, and
the behavioral-parity gate.

**Guardrail:** Students connect supplied components; they do not manually solve
the client task or rewrite the loops, policies, hooks, server, or tests.

## R5 — Exercise solution and captured comparison

Primary local sources:

- `module-6-prod-harness/solution/README.md`
- `module-6-prod-harness/solution/python/loop/configured_agent_loop.py`
- `module-6-prod-harness/solution/hermes/configured_plugin.py`
- `module-6-prod-harness/solution/harness-comparison.md`
- saved `solution/python/runs/*` and `solution/hermes/runs/*` artifacts

**Relevant use:** Shows the completed adapters, captured client implementations,
saved trace behavior, deterministic verification, and maintainability analysis.

**Guardrail:** The captured clients, cycle counts, failure paths, durations,
models, and providers describe those runs. They are not a statistically
controlled framework benchmark. Compare ownership only after equivalent
behavior passes.

## Claim-to-source map

| Course claim | Source | Approved phrasing |
| --- | --- | --- |
| Hermes owns generic model/session continuation | R1, R5 | “In this integration, Hermes owns the generic agent lifecycle.” |
| Plugin owns domain policy and evidence | R1 | “The plugin supplies incident-specific tools, skills, controls, oracle, and trace semantics.” |
| Safe rollback is a positive control | R1 | “It proves legitimate work can pass both controls and execute.” |
| Permission precedes safety | R1, R3 | “A denial short-circuits repeat, safety, and handler execution for that proposal.” |
| Completion is state-and-trace based | R1, R3 | “Final prose and exit status do not establish business completion.” |
| Validator is not workflow proof | R1, R2 | “Validation establishes package and registration compatibility; scenarios establish domain behavior.” |
| Exercise clients may differ | R4, R5 | “Textual equality is unnecessary when both satisfy the same required behavior.” |
| Hermes is preferable for the captured growth context | R5 | “The captured solution recommends Hermes when lifecycle components are expected to grow.” |

## Deliberately scoped claims

The collateral does not claim that this repository implements:

- a hosted or highly available production deployment;
- an organization-wide identity or secret-management system;
- durable or concurrent incident-state coordination;
- a complete observability backend;
- plugin release automation, canary rollout, or release rollback;
- security certification; or
- universal superiority of Hermes over a custom loop.

These concerns are named as production extensions, not represented as completed
features.

## Citation and recording policy

1. Treat the checked-out repository as authoritative for course behavior.
2. Show the installed Hermes version beside current CLI claims.
3. Label saved model traces as captured observations.
4. Never call dry run a simulation or runtime test.
5. Never call plugin validation end-to-end proof.
6. Use trace and state for authorization, safety, execution, and completion
   claims.
7. Redact credentials, personal paths, and unrelated profile data.
8. Re-run deterministic tests after any manifest, profile, registration, hook,
   permission, or completion change.
9. Re-run all three live scenarios before publishing behavior claims.
10. Keep incident rollback and harness-release rollback distinct.
