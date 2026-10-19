# Plugin Contract Workbook

Use this workbook before implementing or reviewing a production plugin. Each
row must identify an owner, a runtime boundary, evidence, and a failure mode.

## 1. Runtime ownership

| Responsibility | Owner | Interface | Evidence | Failure if missing |
| --- | --- | --- | --- | --- |
| Model calls and continuation | Hermes | CLI/session lifecycle | Usage record and runtime result | Application accidentally builds a second loop |
| Tool implementation | Plugin | `register_tool` | Registered name plus `tool_result` | Model can request work that has no handler |
| Skill availability | Plugin | `register_skill` | `skill_registered` | Skill path or qualified name is wrong |
| Skill selection | Launcher + Hermes | `--skills` and `pre_llm_call` | `skills_preloaded` | Registered skill never reaches the session |
| Authorization | Plugin | `pre_tool_call` | `permission_decision` | Tool can bypass trusted subject policy |
| Mutation safety | Plugin | `pre_tool_call` after authorization | `hook_decision` | Authorized but invalid state change executes |
| Tool-result observation | Plugin | `post_tool_call` | `tool_result` and evidence update | Completion relies on model claims |
| Completion lifecycle | Hermes | `pre_verify` dispatch and bounded nudges | Verification decision | Loop stops before required outcome |
| Completion criteria | Plugin | Scenario oracle | `completion` and final state | Runtime cannot define domain success |
| Usage accounting | Hermes | `--usage-file` | `usage.json` | Serving work is invisible |

## 2. Package declaration

Complete these fields before validation:

| Contract field | Incident demo value | Review question |
| --- | --- | --- |
| Stable plugin name | `incident-response-demo` | Does the profile and CLI use this exact name? |
| Version | `1.0.0` | Is compatibility managed when interfaces change? |
| Entry point | `__init__.py` by plugin convention | Can validation import it without runtime-only state? |
| Declared tools | Six incident tools | Do declarations exactly match registrations? |
| Declared hooks | Four lifecycle hooks | Are all registered events declared? |
| Required environment | None declared | Which runtime values are still needed for a real session? |
| Dependencies | None declared | Is the standard-library-only claim accurate? |

The demo supports a validation probe that declares capabilities without
executing incident tools. Real registration reads runtime environment paths and
creates the scenario-specific plugin object.

## 3. Activation

The isolated profile must answer three separate questions:

1. Is the plugin enabled?
2. Is its named toolset exposed on the CLI platform?
3. Which unrelated discovery or coding capabilities are disabled?

For this demo:

```yaml
plugins:
  enabled:
    - incident-response-demo

platform_toolsets:
  cli:
    - incident-response-demo

skills:
  project_discovery: false

agent:
  coding_context: "off"
  max_turns: 20
  max_verify_nudges: 4
  verify_on_stop: false
```

Activation does not automatically select skills for a session. The launcher
also passes the two qualified names with `--skills`.

## 4. Capability minimization

| Surface | Included | Excluded | Reason |
| --- | --- | --- | --- |
| Toolsets | Incident plugin only | Unrelated built-ins and plugins | Reduce executable authority |
| Skills | Triage and safe remediation | Project skill discovery | Make model context explicit |
| Workspace | Demo directory | Unrelated repositories | Bound task context |
| Profile | Temporary isolated home | Full user profile | Avoid ambient activation |
| Credentials | Supported inputs needed for provider | Unrelated secrets | Limit credential exposure |

The temporary profile is useful demonstration isolation. It is not a complete
production secret-management design.

## 5. Scenario contracts

| Scenario | Subject | Target | Permission | Safety | Handler | Final state |
| --- | --- | --- | --- | --- | --- | --- |
| Safe | Morgan, incident commander | `checkout-v41` | Allow | Allow | Executes | `checkout-v41` |
| Unauthorized | Sam, support engineer | `checkout-v41` | Deny | Not reached | Does not execute | `checkout-v42` |
| Unsafe | Morgan, incident commander | `checkout-v40` | Allow | Block | Does not execute | `checkout-v42` |

## 6. Release-readiness questions

- Does every declared capability have a deterministic registration test?
- Does every mutation have both an allowed and prevented test?
- Does every denial or block include `executed: false`?
- Are completion checks built from state and trace rather than response prose?
- Are retries and completion nudges bounded?
- Does each scenario start from pristine state?
- Are state, trace, usage, and summary paths isolated by run in a real
  deployment?
- Is there a release rollback plan for the plugin itself, separate from the
  incident rollback tool demonstrated here?

The last two items are production extensions; the local demo overwrites one
ignored `runs/` directory and does not implement a deployment system.
