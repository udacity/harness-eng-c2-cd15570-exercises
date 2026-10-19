# Operating a Production Harness

Instructional collateral for **Module 6: Production Harness Integration and
Operations**.

This package is for instructor review, video recording, slide production, and
exercise alignment. It completes the `INC-2048` story by packaging the
evaluated components from Modules 1–5 as a native Hermes plugin and running
them at explicit lifecycle boundaries.

## Teaching thesis

A production harness is not a larger prompt and not a collection of controls
that merely exist in a repository. It is an owned runtime in which domain
components are registered at the correct boundaries, legitimate work can pass,
unsafe or unauthorized work cannot execute, and authoritative evidence proves
which outcome occurred.

```text
qualified components
        |
        v
package + activate + validate
        |
        v
register at lifecycle boundaries
        |
        v
allow useful work / deny authority / block unsafe state
        |
        v
verify completion from state and trace
        |
        v
operate, test, and evolve with evidence
```

Hermes owns the generic agent lifecycle. The plugin owns incident-specific
tools, skills, permissions, safety invariants, completion criteria, and trace
semantics. Keeping that boundary explicit prevents application code from
silently becoming a second agent runtime.

## The three use cases come first

Every demo run begins with degraded `checkout-v42` and fresh state:

| Scenario | Trusted subject and request | Expected boundary outcome |
| --- | --- | --- |
| `safe-rollback` | Incident commander, last-known-good `checkout-v41` | Execute |
| `unauthorized-rollback` | Support engineer, safe `checkout-v41` | Deny |
| `unsafe-rollback` | Incident commander, non-approved `checkout-v40` | Block |

`safe-rollback` is the positive control. It proves that the harness enables
valid production work rather than achieving safety by blocking everything.

Previewing it with:

```bash
python3 run_demo.py safe-rollback --dry-run
```

prints the resolved Hermes command only. It does not call a model, start a
plugin session, execute a rollback, reset state, or write new run evidence.

## Package map

```text
production_harness/
├── README.md
├── module_overview.md
├── learning_objectives.md
├── scripts/       complete narration for five short lessons
├── slides/        slide-by-slide production storyboards
├── visuals/       architecture and evidence specifications
├── examples/      contracts, pseudocode, tests, and sample evidence
├── references/    annotated repository sources
└── instructor_review.md
```

## Recommended review order

1. Review `module_overview.md` and `learning_objectives.md`.
2. Approve the runtime-versus-plugin ownership boundary.
3. Review the three scenario contracts and lifecycle order.
4. Verify that validation, dry run, real execution, and completion are never
   conflated.
5. Review each script beside its storyboard.
6. Confirm that the exercise compares responsibility and evidence, not model
   personalities, raw line counts, or insignificant timing differences.
7. Resolve `instructor_review.md` before recording.

## Editorial conventions

- **Package** means the plugin manifest, entry point, and implementation files.
- **Activation** means enabling the plugin and exposing its named toolset in a
  runtime profile.
- **Validation** means structural and registration compatibility checks; it is
  not business-workflow proof.
- **Dry run** means command preview only.
- **Permission denial** means the trusted subject is not authorized.
- **Safety block** means the subject is authorized but the proposed state
  transition violates a deterministic invariant.
- **Execution** means the registered handler actually ran.
- **Completion** means the scenario oracle accepted authoritative state and
  boundary evidence.
- **Positive control** means a case that must be allowed and completed.
- **Production evidence** means structured state, trace, usage, and summary
  artifacts—not only final prose or process exit status.

The demo's rollback is an incident-response business operation. It is distinct
from rolling back a software release of the harness itself.

## Repository alignment

The collateral references:

- `demo/README.md`
- `demo/run_demo.py`
- `demo/data.py`
- `demo/plugin_impl.py`
- `demo/components/permissions.py`
- `demo/components/hooks.py`
- `demo/.hermes/plugins/incident-response-demo/plugin.yaml`
- `demo/.hermes/config.yaml`
- `demo/test_demo.py`
- `exercise-prod-harness-starter/README.md`
- `solution/python/loop/configured_agent_loop.py`
- `solution/hermes/configured_plugin.py`
- `solution/harness-comparison.md`

The repository is authoritative for this course version. Hermes interfaces can
change, so instructors should rerun validation and tests in the recording
environment instead of assuming a previously captured CLI surface.
