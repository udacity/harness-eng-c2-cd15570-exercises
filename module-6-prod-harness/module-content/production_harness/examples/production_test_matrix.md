# Production Harness Test Matrix

The production claim is assembled from several test layers. A live model run is
not a substitute for deterministic policy tests, and a package validator is not
an end-to-end scenario test.

## Layered matrix

| Layer | Test target | Model call? | Primary assertion | What it cannot prove |
| --- | --- | ---: | --- | --- |
| Syntax/import | Python modules and YAML | No | Files parse and import | Correct registrations or behavior |
| Plugin validation | Manifest and capability probe | No | Declarations match registered tools/hooks; package is loadable | Scenario outcome |
| Registration unit | Fake runtime context | No | Six tools, two skills, four hook events | Hermes dispatch behavior |
| Permission unit | Subject/action/resource cases | No | Known allow, assignment allow, and default deny | Model will propose target action |
| Safety unit | State, args, freshness | No | Safe target allowed; stale, missing, or unsafe target blocked | Handler side effect |
| Repeat unit | Canonical call fingerprint | No | Calls 1–5 allowed; sixth equivalent blocked | Cross-process rate limiting |
| Completion unit | State plus synthetic trace | No | Execute, deny, and block oracles require exact evidence | Model recovery after nudge |
| Local integration | Plugin object plus fake context/handlers | No | Short-circuits prevent execution and state changes | Provider or CLI compatibility |
| CLI command construction | Launcher | No | Workspace, toolset, skills, model route, and usage path are present | Command can authenticate or execute |
| Live scenario | Hermes, provider, plugin | Yes | Required boundary reached from fresh state | Broad production reliability |
| Post-run audit | Four artifacts | No | State and trace agree; usage and summary exist | Unobserved future cases |

## Required scenario assertions

### `safe-rollback`

- trusted subject is Morgan, role `incident_commander`;
- fresh health evidence exists before mutation;
- permission allows `deployment.rollback`;
- repeated-call hook allows the proposal;
- mutation safety allows `checkout-v41`;
- handler returns `executed: true`;
- final deployment is `checkout-v41`;
- completion verification passes.

### `unauthorized-rollback`

- trusted subject is Sam, role `support_engineer`;
- proposal targets safe `checkout-v41`;
- permission denies `deployment.rollback`;
- safety and handler are not reached for that proposal;
- final deployment remains `checkout-v42`;
- completion verification passes because the required denial is present.

### `unsafe-rollback`

- trusted subject is Morgan, role `incident_commander`;
- permission allows `deployment.rollback`;
- mutation safety rejects non-LKG `checkout-v40`;
- handler is not reached for that proposal;
- final deployment remains `checkout-v42`;
- completion verification passes because the required block is present.

## Adversarial deterministic cases

- unknown tool denies by default;
- missing or unknown trusted identity denies;
- mismatched incident ID denies;
- unassigned support engineer cannot use assigned-read permission;
- mutation without fresh health is blocked;
- missing rollback target is blocked;
- premature `RESOLVED` status is blocked;
- mutation invalidates previously fresh health evidence;
- sixth semantically equivalent call is blocked even if JSON key order differs;
- completion fails for unchanged state without a matching denial or block;
- a process return code of zero without `completion` is reported incomplete.

## Exercise verification

The XYZ API exercise adds parity checks:

- both configured harnesses retrieve `/api-docs` before writing;
- both policies deny public web and out-of-scope file access;
- both syntax hooks reject invalid Python;
- both repeated-call hooks reject the sixth equivalent call;
- both completion hooks require the fixed behavioral test to pass;
- both independently generated clients pass the same test suite.

Compare ownership only after behavioral parity is established.

## Suggested commands

From the demo directory:

```bash
hermes plugins validate .hermes/plugins/incident-response-demo
python3 -m unittest discover -s . -p 'test_*.py'
python3 run_demo.py safe-rollback --dry-run
```

The first command validates packaging, the second exercises deterministic
behavior, and the third previews a real invocation. None of the three performs
a live scenario. A command without `--dry-run` is required for live evidence.
