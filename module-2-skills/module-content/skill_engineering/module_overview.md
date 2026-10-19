# Module Overview

## Module identity

- **Course capability:** Module 2 — Skill Engineering in Harness Loops
- **Exercise:** Progressive skill discovery, loading, and composition
- **Audience:** software developers and AI engineers building agentic systems
- **Target duration:** approximately 32 minutes across five videos
- **Running example:** on-demand incident-response guidance for `INC-2048`

## Why this module exists

Base prompts become difficult to maintain when every request receives every
domain procedure, style guide, exception, and example. Large always-on context
can waste tokens and place irrelevant or conflicting guidance beside the task.
Skills create a modular alternative: keep a compact catalog visible, then load
detailed instructions only when the task calls for them.

The pattern introduces new responsibilities. The model may choose the wrong
skill, miss a relevant one, or request an unknown name. Skill content may be
stale, conflicting, oversized, or malicious. The harness must treat selection
as a proposal, validate it against a trusted catalog, and retain evidence of
what was actually loaded.

Most importantly, skills and hooks solve different problems. A skill explains
how the model should work. A hook controls what the application does at a
defined event boundary. Moving a safety invariant into a skill does not make it
enforced.

## Lesson sequence

| Video | Title | Duration | Central question |
| --- | --- | ---: | --- |
| 1 | Skills as task-specific context | 6:00 | When should guidance become a skill? |
| 2 | Skills are not hooks | 6:15 | Which behaviors are advisory, and which must be enforced? |
| 3 | Author skills that route well | 6:30 | How do metadata and bodies support progressive disclosure? |
| 4 | Add skill loading to the loop | 7:00 | How does the harness safely select, load, and continue? |
| 5 | Test, measure, and govern skills | 6:15 | How do we know a skill helps and remains safe over time? |

**Total target duration:** 32 minutes.

## Narrative arc

### Act 1: Expose context overload

Compare the one-call `basic` path, which supplies all four incident skills,
with a stakeholder-update task that mainly needs communication guidance. Show
that modularity is about relevance and maintainability, not guaranteed quality.

### Act 2: Establish the skills/hooks boundary

Put two paths side by side:

```text
skill: task -> model selects guidance -> model may follow it
hook:  lifecycle event -> harness runs code -> allow/block/transform/log
```

Use safe remediation as the example. A skill can tell the model to verify a
rollback target. A before-tool hook can prevent execution when verification
fails. Production systems often need both.

### Act 3: Design the skill contract

Separate routing metadata from detailed instructions. Write a narrow name and
a description that states what the skill does and when it applies. Put
procedures, evidence rules, edge cases, and examples in the body. Define
conflict, trust, ownership, and version policy.

### Act 4: Engineer the loading loop

Discover from a trusted root, build a catalog without reading bodies into the
prompt, offer a narrow loading interface, validate exact names, return
call-correlated results, and make the final writing call. Bound selection and
handle zero, one, or many valid requests.

### Act 5: Evaluate the system

Test parser and security invariants deterministically. On representative tasks,
measure skill-selection precision and recall, task success, instruction
adherence, tokens, latency, and failure modes. Version skills like code and
retain enough provenance to reproduce a run.

## Skills versus adjacent harness components

| Need | Correct component | Reason |
| --- | --- | --- |
| Reusable domain procedure or style guidance | Skill | Supplies task-specific model context. |
| Fresh or changing facts | Retrieval/tool | Reads authoritative data at run time. |
| Perform an external action | Tool | Connects the model proposal to application code. |
| Deterministically inspect or gate a lifecycle event | Hook | Executes automatically at the wired boundary. |
| Decide who may perform an action | Permission policy | Enforces identity and resource authorization. |
| Judge whether the final candidate meets requirements | Evaluator/check | Produces acceptance evidence. |
| Universal instruction needed on every task | Base instruction | Avoids needless routing and loading. |

## Target architecture

```text
trusted skill root
      |
      v
discover + validate metadata -----> compact catalog
                                        |
request + base instructions ------------+
                                        v
                              selection model cycle
                                        |
                               proposed skill names
                                        v
                          exact allowlist validation
                                /               \
                             reject             load
                                                |
                                      instructions + provenance
                                                v
                                      final model cycle
                                                |
                                     candidate + run metrics
                                                v
                                    independent evaluation
```

Hooks appear later around lifecycle boundaries such as tool execution. They do
not replace the catalog or skill-selection path.

## Activation strategies

Progressive disclosure does not require the model to be the only router. Choose
an activation policy that matches task ambiguity and risk:

| Strategy | Best fit | Main tradeoff |
| --- | --- | --- |
| Explicit user or operator preload | Known workflow or instructor-controlled run | Predictable, but the caller must know the catalog. |
| Deterministic routing | Stable signal such as command, file type, tenant, or task ID | Testable, but brittle when intent is ambiguous. |
| Model-selected loading | Natural-language tasks with overlapping intent | Flexible, but selection is probabilistic and adds a model step. |
| Hybrid routing | Required skills fixed by code; optional skills selected dynamically | Protects required context while retaining flexibility; policy is more complex. |

The Module 2 demo uses model-selected loading so routing is visible. A
production system may use any combination. A safety control that must always
run belongs in a hook, permission layer, or other harness boundary—not in an
optionally activated skill.

## Catalog snapshot and caching policy

Build or refresh catalogs at a declared boundary, such as process startup or a
versioned deployment. Treat one run's catalog as a stable snapshot. If bodies
are cached, key them by immutable version or content hash, enforce size and
encoding limits before caching, and invalidate them when the deployed catalog
changes. Avoid silently reading a different file version between selection and
loading; the run trace should identify the exact content supplied.

## Required production concerns

The complete lesson covers:

- deciding whether content belongs in a skill;
- single-responsibility skill design;
- metadata, naming, descriptions, bodies, examples, and optional resources;
- progressive disclosure and context budgeting;
- discovery from trusted roots and metadata validation;
- exact-name allowlisting and path-traversal resistance;
- selection prompts, closed function schemas, and provider strict mode where
  supported;
- zero, one, multiple, duplicate, malformed, and unknown selections;
- response continuation and removal of the loader after selection;
- instruction precedence and conflicting skills;
- prompt injection, provenance, secret handling, and executable resources;
- cycle, size, token, latency, and cost limits;
- deterministic tests and behavior evaluations;
- routing precision/recall and end-task quality;
- logging, versioning, ownership, rollout, rollback, and deprecation; and
- the boundary between skills, hooks, tools, permissions, retrieval, and
  evaluators.

## Deliberate non-goals

- Claiming that fewer tokens always produce better results.
- Treating model skill selection as deterministic classification.
- Giving skill text authority to bypass permissions or hooks.
- Loading arbitrary paths supplied by the model.
- Executing scripts merely because a skill references them.
- Claiming full conformance with an external skill specification.
- Hiding an extra selection call when reporting latency or cost.

## Completion evidence

Learners should leave with:

1. one well-scoped `SKILL.md`;
2. a metadata-only catalog;
3. an exact-name allowlisted loader;
4. a bounded two-cycle loading path;
5. tests for malformed and adversarial requests;
6. an explicit skills-versus-hooks decision table;
7. a run trace containing selection and provenance; and
8. a paired comparison of quality, context, tokens, and latency.
