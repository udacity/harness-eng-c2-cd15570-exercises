# Module Overview: Production Harness Integration and Operations

## Module purpose

Modules 1–4 built evaluation, skills, deterministic hooks, and trusted
permissions. Module 5 measured their contribution. Module 6 turns the qualified
design into one operable runtime integration.

Students learn where framework responsibility ends and domain responsibility
begins, how to package and activate a plugin, how to attach controls to exact
lifecycle boundaries, and how to prove useful and safe outcomes from
authoritative evidence.

## Prerequisites

Students should already be able to:

- distinguish a model proposal from tool execution;
- explain skills as scoped model context;
- explain hooks as deterministic lifecycle code;
- apply subject-action-resource authorization;
- define a completion oracle from trusted state;
- interpret an ablation result without overgeneralizing it; and
- read Python callbacks, YAML manifests, JSON, and JSONL traces.

## Five-video sequence

| Video | Working title | Central question | Target |
| --- | --- | --- | ---: |
| 1 | From Components to a Production Runtime | Which responsibilities belong to the framework and to the plugin? | 6 min |
| 2 | Package, Activate, and Validate the Plugin | What does each deployment step prove? | 7 min |
| 3 | Wire Controls to Lifecycle Boundaries | Where and in what order must each component run? | 7 min |
| 4 | Prove Useful and Safe Operation | How do positive, denied, and blocked cases establish runtime behavior? | 8 min |
| 5 | Operate and Evolve with Evidence | How should teams test, compare, and maintain the harness? | 7 min |

Approximate total: 35 minutes.

## Conceptual spine

```text
measured requirements
  -> explicit ownership boundary
  -> package contract
  -> profile activation
  -> structural validation
  -> safe command preview
  -> fresh-state scenario execution
  -> ordered permission and hook enforcement
  -> authoritative tool result
  -> completion verification
  -> trace + state + usage + summary
  -> deterministic regression tests
  -> scoped production recommendation
```

## Runtime ownership boundary

| Hermes runtime owns | Incident plugin owns |
| --- | --- |
| Model invocation and continuation | Six domain tool handlers |
| Session and turn lifecycle | Two incident-response skills |
| Hook dispatch | Trusted permission policy |
| Preloaded-skill delivery | Repeated-call and mutation invariants |
| Completion-nudge mechanism | Scenario completion oracle |
| Usage accounting | Domain JSONL evidence semantics |

`run_demo.py` prepares an isolated profile, creates fresh state, invokes Hermes,
and derives the result summary. It is launch support, not another model loop.

## Three proof scenarios

The cases isolate authority and safety while keeping initial incident state
controlled:

```text
authorized + safe   -> permission allow -> safety allow -> execute
unauthorized + safe -> permission deny  -> no safety check -> no execution
authorized + unsafe -> permission allow -> safety block   -> no execution
```

The first case is indispensable. Denial and blocking cases alone cannot show
that an operator can recover a service through the harness.

## Packaging is not activation

The plugin manifest declares identity, entry point, tools, and hooks. The
runtime profile enables the plugin and exposes its toolset. The launcher
selects the toolset and qualified skills for a session.

These are separate contracts:

1. package declaration;
2. runtime activation;
3. session capability selection; and
4. domain execution.

`hermes plugins validate` checks that the package parses, loads, registers its
declared capabilities, avoids collisions, and passes the validator's security
scan. It does not prove that a model will retrieve fresh evidence, that an
authorized rollback will execute, or that a denied rollback will preserve
state.

## Lifecycle wiring

The plugin registers four lifecycle callbacks:

| Boundary | Domain responsibility |
| --- | --- |
| `pre_llm_call` | Record that selected skills reached the model lifecycle |
| `pre_tool_call` | Permission, repeated-call control, and mutation safety |
| `post_tool_call` | Record authoritative result and update evidence freshness |
| `pre_verify` | Accept completion or return a bounded corrective nudge |

Within `pre_tool_call`, order is policy:

```text
trusted identity
    -> authorization
    -> repeated-call control
    -> mutation safety when applicable
    -> handler execution
```

An unauthorized call must not reach a safety check that could reveal protected
state. A safety block must not reach the handler. Post-tool observation must
never fabricate execution for a denied or blocked proposal.

## Completion is a business decision

Exit code zero means the CLI process returned normally. Final prose means the
model produced text. Neither proves the scenario outcome.

The completion hook reads authoritative state and trace evidence:

- the safe case requires deployment `checkout-v41` and a successful rollback;
- the unauthorized case requires deployment to remain `checkout-v42` and a
  permission denial for rollback; and
- the unsafe case requires deployment to remain `checkout-v42` and a failed
  rollback hook decision. The live scenario and deterministic test confirm the
  intended `mutation_safety` block. A hardened production oracle should filter
  on that exact hook and its target-validation code.

If evidence is missing, `pre_verify` returns `continue`. The runtime delivers a
corrective nudge and keeps the session running, within configured turn and
verification limits.

## Evidence model

Each real run produces four complementary artifacts:

| Artifact | Authority |
| --- | --- |
| `runs/incident.json` | Final domain state |
| `runs/run.jsonl` | Ordered lifecycle decisions and results |
| `runs/usage.json` | Runtime model, call, token, and cost evidence |
| `runs/run-result.json` | Compact derived scenario summary |

No single artifact answers every question. The summary is convenient but
derived; state and trace establish the business result.

## Exercise transfer

The exercise asks students to connect equivalent supplied components to a
hand-built Python loop and to Hermes. Both agents independently implement the
same missing XYZ API client after retrieving current local documentation.

The comparison is about ownership:

- the Python solution owns model continuation, dispatch, hook order,
  completion retries, tracing, and usage aggregation;
- the Hermes solution owns adapters and domain rules while the framework owns
  the generic lifecycle.

Both generated clients must pass the same behavioral test. Textual equality is
not required. Small observed timing differences and raw line counts do not
support a framework-performance conclusion.

## Assessment evidence

Students demonstrate mastery by producing:

- a framework-versus-plugin responsibility map;
- a valid manifest, activation profile, and session capability selection;
- lifecycle registrations with explicit ordering and fail-closed behavior;
- positive, denied, and blocked scenario evidence from fresh state;
- completion logic based on trusted state and trace facts;
- deterministic tests for allowed and prevented paths;
- a comparison of hand-built and framework-owned lifecycle responsibilities;
  and
- a scoped operational recommendation with limitations.
