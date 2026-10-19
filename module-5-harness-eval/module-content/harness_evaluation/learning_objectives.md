# Learning Objectives

By the end of Module 5, learners will be able to:

1. **Distinguish model evaluation from harness evaluation** by identifying the
   model, skills, permissions, hooks, tools, online critic, and offline judge as
   separate units with separate evidence.
2. **Construct a controlled ablation matrix** in which each `no-*`
   configuration changes exactly one component relative to `full` while the
   model, task, identity, starting state, and business tools remain fixed.
3. **Design component-target tasks** that expose the distinct responsibility of
   skills, an online evaluator, hooks, and permissions rather than relying on
   easy tasks where every configuration looks equivalent.
4. **Separate proposal, enforcement, execution, and evaluation evidence** so a
   tool request or fluent response cannot be mistaken for a completed, safe,
   authorized action.
5. **Combine deterministic and model-based oracles** by using code for exact
   state, safety, permission, coverage, and response-policy requirements while
   reserving model judgment for open-ended prose qualities.
6. **Require probe and measurement coverage** before drawing a conclusion,
   including proof that the relevant proposal reached both the protected and
   ablated boundaries.
7. **Aggregate without hiding failures** by reporting success rate, minimum as
   well as mean quality, invalid and unauthorized executions, coverage, and
   task-level results.
8. **Separate serving cost from experiment overhead** so the online critic and
   revision count against the deployed configuration while the blind judge does
   not distort serving-cost comparisons.
9. **Apply qualification before optimization** by rejecting any configuration
   that fails a hard requirement, then ranking only qualifying configurations
   by component count and complete serving-cost measurements.
10. **Write a scoped recommendation** that states what the observed study
    establishes, its limitations, and the repeated, held-out, adversarial, and
    human-calibrated evaluation needed next.

## Observable mastery criteria

A learner has met the objectives when they can answer from raw trial evidence:

- Which single component changed between two configurations?
- Which task exercised that component's production responsibility?
- Did the model submit the proposal required to test the boundary?
- What did enforcement decide, and what actually executed?
- Which result came from deterministic code and which from a model judge?
- Is every required measurement present?
- Does the configuration qualify before cost is considered?
- Which conclusion is supported, and which broader claim is not?

## Misconceptions to correct

- “Full beat bare, so every component is necessary.”
- “The highest average quality score is the winner.”
- “If the model did not try the unsafe action, the hook was proven effective.”
- “A blind judge can replace deterministic safety or authorization checks.”
- “A post-hoc observer prevented the failure it detected.”
- “Missing measurements mean zero failures.”
- “The online critic and offline judge have the same role and cost.”
- “One repetition proves a stable production effect.”
- “The cheapest configuration is minimum viable even when it fails a gate.”
- “A recommendation-ready study proves universal production safety.”
