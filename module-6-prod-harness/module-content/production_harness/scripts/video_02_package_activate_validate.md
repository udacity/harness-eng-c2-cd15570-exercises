# Video 2 — Package, Activate, and Validate the Plugin

**Target runtime:** 7 minutes  
**Teaching purpose:** Separate package declaration, runtime activation,
validation, session selection, and real execution.

## Opening

A plugin can be implemented correctly and still be unavailable to a session.
It can also load successfully and still behave incorrectly for the business
task. Module 6 treats packaging, activation, validation, selection, and
execution as distinct contracts.

## Declare the package

Open `.hermes/plugins/incident-response-demo/plugin.yaml`.

The manifest names and versions the package, identifies its purpose, declares
six tools, and declares four hook events. Those declarations create a contract
that the validator can compare with registration.

The six tools read incident data, service health, deployment history, and
logs, or mutate deployment and incident status. The four hooks correspond to
pre-model, pre-tool, post-tool, and pre-verification boundaries.

The manifest does not implement any tool. It does not enable the plugin. It
does not grant authority. It tells the runtime what package capabilities should
exist after loading.

Open the plugin entry point and `plugin_impl.py`. During a real run,
`IncidentResponsePlugin.register()` registers handler functions, two skills,
and four callbacks. For validation, an environment-free registration path
declares the same capabilities without trying to load scenario state or execute
a tool. This keeps the capability probe deterministic and side-effect free.

## Activate the package

Open `.hermes/config.yaml`.

The `plugins.enabled` list activates `incident-response-demo`. The CLI platform
toolset list exposes its named toolset. These are independent from the
manifest: declaration answers what the package provides; activation answers
what this runtime profile will use.

The profile also disables project skill discovery and coding context. It bounds
the session to 20 turns and at most four completion nudges. These settings
reduce ambient capability and prevent a verification failure from producing an
unbounded loop.

The launcher still has one more choice. It passes
`--toolsets incident-response-demo` and two qualified names through `--skills`.
A skill can therefore be registered but not selected for a particular session.
The trace preserves both facts.

## Validate the structure

From the demo directory, run:

```bash
hermes plugins validate .hermes/plugins/incident-response-demo
```

Walk through the output. The manifest parses and includes the required fields.
Environment variable declarations follow the expected form. The entry point is
loadable. The capability probe calls `register()` in isolation. Declared tools,
hooks, and middleware match what registration supplies. The validator reports
dependency, collision, and security-scan results.

Then state the boundary of this evidence clearly:

> Validation proves that the plugin is structurally compatible with this
> runtime's plugin contract. It does not prove an incident rollback workflow.

No model has gathered evidence. No trusted user has been authorized. No
mutation invariant has been tested against `checkout-v40`. No deployment state
has changed. Those claims require deterministic behavior tests and live
scenario evidence.

## Preview the invocation

Now run:

```bash
python3 run_demo.py safe-rollback --dry-run
```

`safe-rollback` chooses the positive-control use case. `--dry-run` previews how
that case would be launched. It does not run it.

The command contains:

- `-z` for a one-shot task;
- `--usage-file` for runtime usage evidence;
- `--in` for the task workspace;
- `--model` and `--provider` for a pinned inference route;
- `--toolsets` for the incident capability surface; and
- `--skills` for the two qualified plugin skills.

The dry run may resolve the configured executable and model route, but it does
not create a runtime plugin session, call the model, reset the incident, execute
a tool, or write new evidence.

Use dry run as a configuration inspection tool. Do not narrate it as a safety
simulation or a rollback rehearsal.

## Isolate the runtime profile

For a real run, `run_demo.py` creates a temporary Hermes home. It copies the
plugin and the demo configuration, carries only supported provider credential
inputs, prepares fresh incident state, invokes Hermes, and removes the temporary
profile afterward.

This reduces interference from unrelated plugins, project skills, and profile
settings. The CLI sees only the intended toolset and selected skills.

Temporary-profile isolation is useful evidence for this demo. It is not a full
secret-management or multi-tenant isolation solution. Production teams still
need a proper credential store, runtime identity, filesystem boundaries, and
artifact retention policy.

## Four gates, four questions

Summarize the distinction:

```text
manifest     What should the package provide?
profile      What is enabled for this runtime?
CLI flags    What is selected for this session?
scenario     Does the business behavior actually hold?
```

Validation addresses the first question and part of compatibility. Dry run
lets us inspect the second and third as resolved command inputs. Only tests and
real scenario runs answer the fourth.

## Closing

The plugin is declared, activated, structurally validated, and selected through
an explicit command. None of those stages should be skipped, and none should be
credited with proof it does not supply.

Next, we will trace the four callbacks and the exact short-circuit order that
prevents unauthorized or unsafe proposals from reaching business tools.

## On-screen repository anchors

- `demo/.hermes/plugins/incident-response-demo/plugin.yaml`
- `demo/.hermes/plugins/incident-response-demo/__init__.py`
- `demo/.hermes/config.yaml`
- `demo/plugin_impl.py`: `register()` and validation registration
- `demo/run_demo.py`: command construction and isolated profile
