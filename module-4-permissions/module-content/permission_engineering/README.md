# Permission-Aware Tool Access for Production Harness Loops

Instructional collateral for **Module 4: Permissions and Authorization**.

This package is for instructor review, video recording, slide production, and
exercise alignment. It uses the `INC-2048` incident-response demo as its
running example and transfers the design to the municipal permit exercise.

## Teaching thesis

A tool schema describes a capability. It does not prove that the authenticated
person or workload has authority to use that capability. A production harness
must derive tool access from the application's real permission model and must
authorize every proposed invocation before execution.

Two controls work together:

```text
trusted identity + production entitlements
                    |
                    v
        expose the smallest useful tool catalog
                    |
                    v
model proposes one call -- not yet an action
                    |
                    v
authorize current subject + action + resource + context
              /                         \
           DENY                         ALLOW
             |                            |
      no side effect              continue to safety
```

Catalog filtering reduces accidental or adversarial access, but it is not the
security boundary. Resource ownership, tenant membership, state, policy
changes, and revocation can be known only at invocation time. The dispatcher
therefore denies by default and performs a fresh decision for every call.

The model never authenticates the user, assigns a role, expands a permission,
or overrides a denial. Those decisions come from trusted production systems.

## Package map

```text
permission_engineering/
├── README.md
├── module_overview.md
├── learning_objectives.md
├── scripts/       complete narration for five short lessons
├── slides/        slide-by-slide production storyboards
├── visuals/       diagram, chart, and asset specifications
├── examples/      policy design, catalog shaping, enforcement, and tests
├── references/    annotated repository and security sources
└── instructor_review.md
```

## Recommended review order

1. Read `module_overview.md` and `learning_objectives.md`.
2. Approve the distinction between capability, authentication, authorization,
   safety, and execution.
3. Review `examples/permission_design_workbook.md`.
4. Review the catalog-shaping and execution-boundary examples.
5. Review each script beside its matching storyboard.
6. Resolve `instructor_review.md` before recording.

## Editorial conventions

- **Authenticated principal** means the trusted user or workload identity
  resolved outside model-controlled text.
- **Entitlement** means a production grant associated with that principal.
- **Tool exposure** means inclusion in the tool catalog sent to the model.
- **Tool proposal** means a model-produced call that has not executed.
- **Authorization** means deciding whether the subject may perform the action
  on the resource under the current context.
- **Enforcement point** means the application boundary that prevents execution
  when the authorization decision is not `ALLOW`.
- **Deny by default** means missing rules, malformed inputs, unknown tools,
  policy errors, or unusable decisions do not grant access.
- **Least privilege** means granting only the access required for the assigned
  production task, for no longer than required.

Live model behavior must be described as observed. Sample decisions and
metrics are illustrative and must not be presented as benchmark data.

## Repository alignment

The narration references:

- `demo/data.py`
- `demo/permissions.py`
- `demo/agent.py`
- `demo/tools.py`
- `demo/hooks.py`
- `demo/scenarios/*.json`
- `exercise-permisions-starter/INSTRUCTIONS.md`
- `exercise-permisions-starter/test_permissions.py`
- `solution/permissions.py`
- `solution/agent.py`

The demo deliberately exposes the same business tools in both modes to isolate
the value of runtime authorization. The production extension taught here is to
also minimize the catalog from trusted entitlements. Runtime authorization is
still required and remains the authoritative enforcement boundary.
