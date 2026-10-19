# Diagram Concepts

## D1 — Context overload versus selective loading

**Purpose:** Establish why skill routing exists without promising quality gains.

**Composition:**

- Left: one stakeholder task enters a prompt containing four complete skills.
- Right: the same task sees four short descriptions, selects communications,
  then receives one complete skill.
- Bottom: tradeoff labels—context relevance, model cycles, routing risk.

**Avoid:** A green winner badge. The measured result decides the tradeoff.

## D2 — Skills and hooks split screen

**Purpose:** Make the module's central distinction memorable.

```text
SKILL                                  HOOK
task match                             lifecycle event
    |                                      |
load instructions                      run harness code
    |                                      |
model proposes                         allow/block/transform/log
```

Use a dotted arrow from skill to model behavior and a solid gate for the hook.

## D3 — One rollback rule, two layers

**Purpose:** Show complementary roles.

- Skill lane: “verify last-known-good before recommending rollback.”
- Model lane: proposed `rollback_deployment(checkout-v40)`.
- Hook lane: trusted history says v40 is not last-known-good → `BLOCK`.
- Feedback lane: violation returns to model for explanation.

## D4 — Adjacent component map

**Purpose:** Prevent responsibility drift.

Center the model/harness loop. Attach six cards:

- skill: reusable procedure;
- retrieval: fresh data;
- tool: capability/action;
- permission: who may act;
- hook: event-time gate/transform;
- evaluator: final acceptance evidence.

## D5 — Progressive disclosure layers

**Purpose:** Explain staged context.

Three nested folders:

1. metadata—always cataloged;
2. `SKILL.md` instructions—loaded after activation;
3. optional resources—loaded only if supported and required.

Apply a bracket labeled “Module 2 demo” around layers one and two only.

## D6 — Skill authoring anatomy

**Purpose:** Connect routing and execution content.

Use a tall `SKILL.md` card with:

- YAML frontmatter;
- purpose/scope;
- required inputs;
- workflow;
- evidence boundaries;
- edge cases;
- output contract.

Draw the description toward the router and the body toward the writing cycle.

## D7 — Trusted catalog construction

**Purpose:** Visualize pre-runtime validation.

```text
trusted root
  -> immediate SKILL.md candidates
  -> reject symlinks/path escape
  -> parse required metadata
  -> require folder/name identity
  -> reject duplicates
  -> immutable catalog snapshot
```

## D8 — Exact loading boundary

**Purpose:** Show why a model argument never becomes a path.

Put `skill_name="../secret"` and `skill_name="incident_triage"` through an
exact-key lookup. Unknown input exits as a correlated error; known input maps
to a catalog-owned path.

## D9 — Two-cycle conversation

**Purpose:** Show API and loop state.

- Cycle 1 input: base rules + task + catalog + loader schema.
- Cycle 1 output: zero or more calls.
- Harness: validation and call-correlated outputs.
- Cycle 2 input: previous response context + results.
- Cycle 2 tools: none.
- Cycle 2 output: final artifact.

## D10 — Evidence ladder

**Purpose:** Stop students from equating loading with success.

```text
discovered -> selected -> loaded -> reflected in behavior -> output accepted
```

Give every arrow a possible failure label and every stage a separate trace
event.

## D11 — Testing pyramid

**Purpose:** Combine deterministic and behavioral evidence.

- Base: parser, paths, schema, correlation, limits, fallbacks.
- Middle: scripted loop integration tests.
- Top: repeated live routing and end-task evaluations.

Do not imply fewer high-level evaluations are always sufficient; the pyramid
communicates cost and determinism, not a fixed test ratio.

## D12 — Skill lifecycle

**Purpose:** Teach operational governance.

```text
author -> review -> validate -> evaluate -> canary -> promote -> monitor
             ^                                      |
             +--------------- rollback -------------+
```

Place owner, version/hash, source, and deprecation record around the cycle.
