# Module 6 Demo: Running the Incident Harness with Hermes CLI

This demo continues the `INC-2048` incident-response use case from Modules
1–5. Production `checkout-api` is `DEGRADED` with an 18% error rate on
`checkout-v42`; `checkout-v41` is last-known-good, and recovery is not yet
confirmed.

Module 6 packages the accumulated harness as a Hermes plugin and runs it with
the Hermes CLI. Hermes owns the model lifecycle, tool-call continuation,
preloaded skills, hook dispatch, completion nudges, session behavior, and usage
accounting. The repository supplies only the incident-specific extension:

- six scoped incident tools;
- two preloadable incident-response skills;
- trusted subject/action/resource permissions;
- repeated-call and deterministic mutation hooks;
- scenario-specific completion verification; and
- a structured JSONL run trace.

There is one execution path in this demo: Hermes CLI.

## Prerequisites

Confirm that Hermes is installed and has a model/provider configured:

```bash
hermes --version
hermes config get model --json
```

If Hermes is not configured yet, run:

```bash
hermes setup
```

The demo uses only Python's standard library. It does not need a separate API
server or additional packages.

## Validate the plugin

From the demo directory, validate the native plugin package with Hermes:

```bash
cd module-6-prod-harness/demo
hermes plugins validate .hermes/plugins/incident-response-demo
```

The plugin manifest is
`.hermes/plugins/incident-response-demo/plugin.yaml`. Its `register(ctx)` entry
point loads `plugin_impl.py`, where the demo calls Hermes's native extension
methods:

```text
ctx.register_tool(...)   six incident tools in one toolset
ctx.register_skill(...)  incident_triage and safe_remediation
ctx.register_hook(...)   pre_llm_call, pre_tool_call, post_tool_call, pre_verify
```

The isolated profile enables the plugin and exposes its toolset on the CLI
platform through `.hermes/config.yaml`.

## Inspect the real Hermes command

Before making a model call, print the resolved command:

```bash
python3 run_demo.py safe-rollback --dry-run
```

The launcher prints a command with this shape:

```bash
hermes -z '<incident-task-prompt>' \
  --usage-file module-6-prod-harness/demo/runs/usage.json \
  --in module-6-prod-harness/demo \
  --model '<configured-model>' \
  --provider '<configured-provider>' \
  --toolsets incident-response-demo \
  --skills incident-response-demo:incident_triage,incident-response-demo:safe_remediation
```

The flags demonstrate the production CLI surface:

| Flag | Purpose |
| --- | --- |
| `-z` / `--oneshot` | Run one task and print only the final agent response. |
| `--usage-file` | Write model, API-call, token, and estimated-cost evidence even if the run fails. |
| `--in` | Set the task workspace before Hermes builds the session. |
| `--model` and `--provider` | Pin the inference route for this run. |
| `--toolsets` | Expose only the incident plugin's registered tools. |
| `--skills` | Preload the two qualified plugin skills into the session. |

`run_demo.py` is profile-isolation support, not an agent implementation. It
reads the configured model route, copies only supported credential inputs into
a temporary Hermes home, copies the demo plugin and config, initializes fresh
incident state, invokes the command above with `subprocess.run()`, and deletes
the temporary profile afterward. All model/tool iteration remains inside the
Hermes executable.

Set `HERMES_CLI` if the executable is not on `PATH`. Set
`HERMES_SOURCE_HOME` when the configured Hermes profile is somewhere other
than `~/.hermes`.

## Run the three scenarios

### 1. Authorized and safe rollback

```bash
python3 run_demo.py safe-rollback
```

Morgan Chen is an incident commander with `deployment.rollback`. The agent
must retrieve fresh health and deployment evidence before proposing rollback
to `checkout-v41`. Permissions allow the proposal, the mutation hook confirms
that the target is last-known-good, and the tool changes the deployment.

Expected core outcome:

```text
completed            True
final_deployment     checkout-v41
```

### 2. Safe but unauthorized rollback

```bash
python3 run_demo.py unauthorized-rollback
```

Sam Rivera is the assigned support engineer. Assignment permits evidence
reads, but the role does not have `deployment.rollback`. The `pre_tool_call`
permission hook returns a structured denial to the model before the safety
hook or tool can execute.

Expected core outcome:

```text
completed            True
final_deployment     checkout-v42
permission_denials   at least 1
```

### 3. Authorized but unsafe rollback

```bash
python3 run_demo.py unsafe-rollback
```

Morgan is authorized to roll back, but `checkout-v40` is not last-known-good.
The permission decision allows the proposal and the mutation hook then blocks
it. This keeps authorization and deterministic safety as separate decisions.

Expected core outcome:

```text
completed            True
final_deployment     checkout-v42
hook_blocks          at least 1
```

The exact number of extra denied or repeated proposals may vary by model. The
authoritative requirement is that the requested rollback reaches the expected
boundary and the incident state remains consistent with that result.

Use `--model` and `--provider` to override the configured route for one run:

```bash
python3 run_demo.py safe-rollback \
  --model '<model-name>' --provider '<provider-name>'
```

## Follow the Hermes lifecycle

For every proposed tool, the registered `pre_tool_call` hook applies this
order:

```text
model proposes tool
        |
        v
trusted permission decision
   deny | allow
        |   |
        |   v
        | repeated-call hook
        |   |
        |   v
        | mutation safety hook when applicable
        |   block | allow
        |         |
        v         v
structured    registered tool executes
non-execution     |
result            v
              post_tool_call records result and evidence
                    |
                    v
              Hermes continues the model turn
```

When the model attempts to finish, `pre_verify` checks authoritative incident
state and boundary evidence. If the requested rollback has not executed, been
denied, or been blocked as expected for that scenario, the hook returns
`action: continue`. Hermes delivers the corrective nudge and keeps the session
running. A passing verification writes the final `completion` event.

## Inspect the evidence

Each run resets and writes four ignored artifacts:

```text
runs/incident.json     authoritative final incident state
runs/run.jsonl         skills, permissions, hooks, tools, and completion events
runs/usage.json        Hermes token, call, model, and estimated-cost record
runs/run-result.json   compact scenario summary
```

Pretty-print the compact results and usage:

```bash
python3 -m json.tool runs/run-result.json
python3 -m json.tool runs/usage.json
```

Follow the ordered lifecycle evidence:

```bash
sed -n '1,240p' runs/run.jsonl
```

Useful trace events include:

| Event | What it proves |
| --- | --- |
| `run_started` | Scenario, trusted identity, and initial deployment were bound before tool use. |
| `skill_registered` | The plugin made an exact skill available to Hermes. |
| `skills_preloaded` | The CLI's `--skills` selection reached the model lifecycle. |
| `permission_decision` | The trusted role/action/resource rule ran before each tool. |
| `hook_decision` | Repetition, mutation safety, or completion verification ran at its lifecycle boundary. |
| `tool_result` | The registered tool's authoritative execution result returned to Hermes. |
| `completion` | `pre_verify` accepted the scenario outcome. |

## What to show during the classroom demo

1. Run `hermes --version` and `hermes config get model --json`.
2. Open `plugin.yaml` and `.hermes/config.yaml` to distinguish packaging from activation.
3. Open `plugin_impl.py` and locate `register_tool`, `register_skill`, and `register_hook`.
4. Run `python3 run_demo.py safe-rollback --dry-run` and explain every CLI flag.
5. Run `safe-rollback` and follow allow → safety pass → execution → verification.
6. Open `runs/usage.json` to show evidence supplied directly by Hermes.
7. Run `unauthorized-rollback` and follow the permission short circuit.
8. Run `unsafe-rollback` and follow authorization allow → safety block.
9. Open `runs/run.jsonl` and verify that disabled or skipped work is never described as executed.
10. End at `pre_verify`: the harness, not the final prose, decides whether the run is complete.

## Connection to the exercise

The exercise uses an XYZ API client task, while this demo keeps the course's
incident-response story. The implementation pattern transfers directly:

| Demo | Exercise |
| --- | --- |
| Incident tools registered in one named toolset | Register the supplied scoped file, local HTTP, and test tools. |
| `incident_triage` and `safe_remediation` registered with qualified names | Register the supplied `xyz-api-client` skill. |
| Permission logic attached to `pre_tool_call` | Apply the supplied default-deny XYZ policy before tools. |
| Result evidence attached to `post_tool_call` | Let the XYZ policy observe successful `/api-docs` retrieval. |
| Mutation checks in `pre_tool_call` | Attach the supplied repeated-call hook before execution. |
| Scenario oracle in `pre_verify` | Attach the supplied behavioral-test completion hook. |
| `--toolsets`, `--skills`, and `--usage-file` | Invoke the configured Hermes task and preserve run evidence. |

The task-specific policy changes, but the production-harness responsibility is
the same: register the supplied components at the correct Hermes lifecycle
events and let Hermes own session execution.

## Deterministic tests

The tests do not make model calls:

```bash
python3 -m unittest discover -s . -p 'test_*.py'
```

They cover plugin registration, manifest/profile activation, CLI command
construction, skill preloading evidence, trusted permissions, safe execution,
permission denial, hook blocking, repeated-call limits, completion nudges,
state isolation, and trace contents.

## Repository map

```text
demo/
├── .hermes/
│   ├── config.yaml                         # isolated Hermes activation
│   └── plugins/incident-response-demo/
│       ├── plugin.yaml                     # native plugin manifest
│       └── __init__.py                     # Hermes register(ctx) entry point
├── components/
│   ├── hooks.py                            # repetition, safety, verification, trace
│   ├── permissions.py                      # trusted authorization policy
│   └── skills/                             # two registered SKILL.md files
├── data.py                                 # identities, scenarios, pristine incident
├── incident_tools.py                       # six simulated incident operations
├── plugin_impl.py                          # Hermes component connections
├── run_demo.py                             # isolated profile + Hermes CLI invocation
├── test_demo.py                            # deterministic lifecycle tests
└── runs/                                   # generated evidence, ignored by Git
```
