# Learning Objectives

## Module-level objectives

By the end of this module, learners will be able to:

1. **Define a skill precisely.** Describe a skill as reusable model-facing
   guidance, not as a guarantee, permission, business action, or evaluator.
2. **Distinguish skills from hooks.** Explain that skills are selected context
   the model may follow, while hooks are harness-owned callbacks that execute at
   defined lifecycle events.
3. **Choose the correct harness component.** Place guidance, fresh data,
   actions, deterministic gates, authorization, and final acceptance in skills,
   retrieval/tools, hooks, permissions, and evaluators respectively.
4. **Design a routable skill.** Write narrow metadata that supports selection
   and a body containing the detailed procedure, evidence boundaries, edge
   cases, and output expectations.
5. **Apply progressive disclosure.** Expose metadata first, full instructions
   after activation, and supporting resources only when needed.
6. **Build safe discovery and loading.** Discover from a trusted root, reject
   malformed metadata and duplicates, allowlist exact names, and preserve
   source provenance.
7. **Integrate skills into a model loop.** Implement selection, function-call
   handling, correlated tool results, conversation continuation, and a final
   no-loader writing cycle.
8. **Handle non-happy paths.** Define behavior for zero, multiple, duplicate,
   malformed, unknown, oversized, conflicting, or unavailable skills.
9. **Secure the skill supply chain.** Treat skill packages as reviewed,
   versioned dependencies; prevent arbitrary file access, secret leakage,
   instruction injection, and implicit code execution.
10. **Test and evaluate skill value.** Combine deterministic integration tests
    with representative task evaluations and measure routing accuracy, end-task
    quality, context size, tokens, latency, and failures.
11. **Operate skills over time.** Assign ownership, log versions or hashes,
    stage rollouts, detect regressions, and support rollback and deprecation.

## Lesson-level objectives

### Video 1 — Skills as task-specific context

Learners can:

- identify guidance that belongs in a skill rather than the base prompt;
- explain context overload and progressive disclosure;
- distinguish activation, loading, and instruction following; and
- explain why selecting a skill does not prove the final output is correct.

### Video 2 — Skills are not hooks

Learners can:

- compare model-facing advice with harness-enforced behavior;
- place a safety procedure in a skill and its non-negotiable invariant in a
  hook;
- explain why the model should not control whether a required hook runs; and
- distinguish skills from tools, permissions, retrieval, and evaluators.

### Video 3 — Author skills that route well

Learners can:

- write discriminative names and descriptions;
- structure detailed bodies for model use;
- define precedence and conflict behavior;
- separate stable procedures from volatile facts; and
- identify specification differences between the course demo and broader
  Agent Skills formats.

### Video 4 — Add skill loading to the loop

Learners can:

- build a metadata-only catalog;
- validate exact allowlisted names and reject path traversal;
- parse zero or more model requests and return correlated results;
- continue the response into a no-loader writing cycle; and
- bound cycles, selected count, and loaded content size.

### Video 5 — Test, measure, and govern skills

Learners can:

- test discovery, routing isolation, loading, and failure handling;
- calculate routing precision and recall against task labels;
- compare skill-enabled and baseline end-task outcomes;
- separate serving metrics from evaluator overhead; and
- define ownership, provenance, rollout, rollback, and deprecation controls.

## Suggested knowledge checks

1. A rule says that refunds above $500 must never execute without approval. Is
   that rule sufficient in a skill? What component must enforce it?
2. A skill description says only “helps with incidents.” Why will routing be
   unreliable, and how should the description change?
3. The model requests `../../secrets.env` as a skill name. What should the
   loader return, and what must it never do?
4. The model selects no skill. Should the harness crash, force an arbitrary
   skill, or continue under an explicit fallback policy?
5. A selective run loads fewer skill characters but makes an extra model call.
   Which measurements are needed before declaring it better?
6. Two selected skills disagree about tone. Where should precedence be
   declared, and what evidence should the run log retain?

## Performance assessment

A learner demonstrates mastery by producing a harness that:

- discovers valid skills without placing bodies in the routing prompt;
- exposes a narrow `load_skill` interface;
- loads only exact catalog entries from a trusted root;
- supports zero, one, and multiple requests;
- returns controlled errors for malformed or unknown requests;
- removes the loading interface before final writing;
- records selected names, source paths or IDs, versions or hashes, and size;
- includes deterministic tests for the loading boundary;
- evaluates selection and final-output behavior on representative tasks; and
- explains which requirements still need hooks, permissions, tools, or an
  evaluator.
