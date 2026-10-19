# Video 5 — Operate and Evolve with Evidence

**Target runtime:** 7 minutes  
**Teaching purpose:** Build the layered verification strategy, transfer the
pattern to the exercise, and make a scoped maintainability recommendation.

## Opening

A successful live run is evidence, but it is expensive, variable, and narrow.
A production harness needs a verification portfolio that catches deterministic
regressions quickly and reserves model runs for true integration behavior.

## Layer the tests

Begin with plugin validation. It catches malformed manifests, registration
mismatches, load failures, declared-capability drift, collisions, and the
validator's security findings.

Then run deterministic tests:

```bash
python3 -m unittest discover -s . -p 'test_*.py'
```

The demo tests make no model calls. They verify registration, manifest/profile
activation, skill-preload evidence, safe execution, permission denial, safety
blocking, completion nudges, trace contents, policy decisions, fresh-evidence
requirements, the sixth equivalent-call block, initially incomplete scenarios,
and CLI command construction.

These tests are fast because trusted code controls the inputs. They should
cover every authorization and safety branch, especially fail-closed paths.

Live scenarios add the remaining question: can a real model, provider, runtime,
plugin, and task prompt reach the required boundaries together? Keep those runs
for integration qualification, release confidence, and periodic monitoring.

## Diagnose by boundary

When a run fails, start with the missing evidence rather than the final answer.

If `skills_preloaded` is absent, inspect qualified skill selection and the
pre-model callback. If no rollback permission decision exists, inspect whether
the model proposed the exact action and resource. If permission denies the safe
case, inspect trusted identity and resource binding. If safety blocks
`checkout-v41`, inspect fresh health and deployment history. If the tool
executes but completion fails, reconcile state mutation with the oracle.

Boundary-specific evidence shortens the path from symptom to owner.

## Transfer to the exercise

The exercise changes the business domain from incident rollback to generating
an XYZ API client, but preserves the integration pattern.

Both harnesses receive equivalent supplied skills, hooks, permissions, tools,
and an incomplete client. Both agents must retrieve the fictional current API
contract from local `/api-docs`, write only the assigned client, and pass the
same fixed behavioral test.

The hand-built Python loop uses connection classes to add the skill before the
first model call, run permission and repeat checks before tools, run syntax
checks after writes, and verify completion before accepting a final response.
That application also owns argument parsing, dispatch, result delivery, model
continuation, cycle limits, trace recording, and usage aggregation.

The Hermes integration registers the same responsibilities at native
lifecycle events. It still needs a real adapter, tool registration, skill
registration, policy state, trace translation, profile activation, and an
isolated runner. Hermes owns the generic session and continuation lifecycle.

## Compare behavior before effort

The two generated clients need not be textually identical. One captured client
used `requests`; the other used Python's standard library. Both passed the same
behavioral test. That is the parity gate.

Only after parity should students compare integration effort:

- Who owns tool dispatch and continuation?
- Where is hook order enforced?
- How is completion retried and bounded?
- What evidence identifies denied and blocked calls?
- What must change when a new hook or tool is added?
- Which framework and version become operational dependencies?

Do not rank the approaches by raw line count. A runner may contain isolation
and process-management code that a custom loop does not. Do not infer a
performance winner from a few milliseconds, especially when different models
or providers were used. Compare responsibilities and measured behavior.

## The scoped conclusion

The captured exercise result supports Hermes for a production harness expected
to gain tools, policies, and lifecycle controls. Native events make boundaries
explicit while the framework owns difficult continuation state.

A hand-built loop remains reasonable for a small, tightly controlled workflow
that needs unusual orchestration or minimal framework dependency. Its cost is
that the application team owns more security-sensitive ordering and state.

That is a contextual recommendation, not a universal rule.

## Beyond the local demo

Before a real release, add concerns that this repository intentionally does not
implement:

- version compatibility and staged plugin rollout;
- durable per-run artifact storage and correlation IDs;
- production identity and secret management;
- concurrency controls for mutable incident state;
- metrics and alerts for denials, blocks, retries, incomplete runs, latency,
  token use, and cost;
- redaction and retention for prompts, arguments, results, and traces;
- dependency and supply-chain review;
- a release rollback plan for the harness plugin; and
- runbooks for runtime, provider, tool, and state-store failures.

Keep the terminology clear: the demo's `safe-rollback` changes an application
deployment during an incident. Rolling back the harness plugin itself is a
different release operation.

## Closing

A production harness has explicit owners, bounded lifecycle events, positive
and negative proof, authoritative completion, and evidence that supports both
debugging and improvement.

The final design is not “Hermes plus every possible control.” It is a measured
set of domain controls connected to a runtime that can execute legitimate work,
prevent the wrong work, and prove the difference.

## On-screen repository anchors

- `demo/test_demo.py`: deterministic regression coverage
- `exercise-prod-harness-starter/README.md`: student task and parity criteria
- `solution/python/loop/configured_agent_loop.py`: hand-built ownership
- `solution/hermes/configured_plugin.py`: native lifecycle adapter
- `solution/harness-comparison.md`: captured evidence and scoped conclusion
