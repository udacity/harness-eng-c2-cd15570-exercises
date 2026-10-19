# Instructor Review Packet

## Review status

This packet is ready for technical, instructional-design, evaluation-method,
and visual review. Resolve every blocking item before recording.

## Decisions requiring approval

### 1. Central thesis

Approve this exact statement:

> Keep the smallest measured harness that satisfies every declared requirement
> with complete evidence. Each component must earn its place through a target
> task and controlled ablation.

### 2. Scope of the captured result

The recorded result contains one repetition across six configurations and five
tasks. Approve the label “captured teaching result” and reject “production
benchmark,” “statistically proven,” or “universally required architecture.”

### 3. Demo and exercise thresholds

The incident demo uses 100% task success. The returns exercise solution uses
90%. Confirm that scripts identify thresholds as application-specific and do
not blend them.

### 4. Judge claims

Approve the split:

- deterministic code is authoritative for exact trace, state, safety,
  permission, policy, and coverage facts;
- the blind model judge assesses open-ended response quality;
- human labels calibrate the automated judge; and
- no single quality score overrides a hard requirement.

### 5. Shadow observation

Approve the terms “read-only observer” and “post-hoc detection.” Never call an
observed invalid action blocked when the ablated tool actually executed.

## Technical accuracy checklist

- [ ] The matrix contains full, four one-switch ablations, and bare.
- [ ] Each named `no-*` differs from full by exactly its named component.
- [ ] Every trial starts from fresh incident state.
- [ ] The complete one-run incident plan has 30 trials.
- [ ] The default seed is recorded as `15570`.
- [ ] Skills target Payments Runtime and `PR-7`.
- [ ] The evaluator target uses the exact stakeholder response policy.
- [ ] The hook target proposes non-last-known-good `checkout-v40`.
- [ ] The permission target proposes safe but unauthorized `checkout-v41`.
- [ ] Authorization precedes hooks, and hooks precede tool execution.
- [ ] Disabled enforcement says `NOT PERFORMED`.
- [ ] The online critic and revision count as serving cost.
- [ ] The blind judge counts as experiment overhead.
- [ ] Readiness checks plan keys, duplicates, scope, and target probes.
- [ ] Qualification precedes component and serving-cost ranking.

## Result-accuracy checklist

- [ ] Captured values match the current generated report.
- [ ] `full`: 100%, 5.00, invalid 0, unauthorized 0.
- [ ] `no-skills`: 80%, 5.00, specialized knowledge failure.
- [ ] `no-evaluator`: 80%, 4.76, response-policy failure.
- [ ] `no-hooks`: 80%, 4.56, one invalid execution.
- [ ] `no-permissions`: 80%, 4.56, one unauthorized execution.
- [ ] `bare`: 20%, 4.12, one invalid and one unauthorized execution.
- [ ] Only `full` is described as qualifying for the captured study.
- [ ] Fixture values in `harness-evaluation.md` are not mixed with live report
      values.

## Evaluation-method checklist

- [ ] Full-to-ablation pairs, not full-to-bare, support attribution.
- [ ] Target tasks exercise non-substitutable responsibilities.
- [ ] Probe coverage is required on protected and ablated paths.
- [ ] Missing measurements remain unavailable.
- [ ] Mean quality is shown with minimum/task-level outcomes.
- [ ] Hard safety and authority gates cannot be offset by averages or cost.
- [ ] Repetition, held-out cases, adversarial cases, and human calibration are
      named as next steps.
- [ ] Passing the study is not presented as universal safety assurance.

## Instructional-design checklist

- [ ] Video 1 establishes system-level evidence before metrics.
- [ ] Video 2 demonstrates why bare is not a causal comparison.
- [ ] Video 3 explains deterministic versus model-based oracles.
- [ ] Video 4 teaches readiness and qualification before ranking.
- [ ] Video 5 explains every captured ablation result and its limitation.
- [ ] Students see one counterintuitive example: 5.00 quality with task failure.
- [ ] Students see one safety/authority distinction: safe v41 but unauthorized.
- [ ] Every chart includes denominators, coverage, and result scope.

## Recording checklist

- [ ] Run tests before recording.
- [ ] Run or stage the complete model study before the live presentation.
- [ ] Open raw CSV before the generated report.
- [ ] State model, judge model, seed, repetitions, tasks, and configurations.
- [ ] Narrate actual current report values if they differ from the captured
      script.
- [ ] Do not show `.env`, API keys, user home paths, or credentials.
- [ ] Do not call a model refusal hook or permission prevention.
- [ ] Do not call a shadow decision serving enforcement.
- [ ] Use `not requested`, `not performed`, `denied`, `blocked`, and `executed`
      precisely.
- [ ] Label all synthetic and fixture visuals.

## Suggested live sequence

1. Open `config.py`; verify one-switch differences.
2. Open the four target scenarios; connect each to one responsibility.
3. Run or reveal the complete `compare --scenario all` study.
4. Open `results.csv`; inspect one row and coverage fields.
5. Trace exact task success in `score_deterministic()`.
6. Compare online critic and blind judge in `experiment.py`.
7. Trace target-probe readiness in `_study_readiness()`.
8. Trace hard qualification and cost ranking.
9. Open the generated report and explain each ablation pair.
10. End with limitations and the repeated held-out next experiment.

## Discussion prompts

1. Which requirements should be deterministic oracles in your system?
2. What target task would expose each proposed harness component?
3. What does a model refusal prove, and what boundary remains untested?
4. Which metrics are hard gates rather than optimization goals?
5. What would make a blind judge non-blind?
6. How will you calibrate automated judgment against experts?
7. What is serving cost, and what is experiment overhead?
8. What new production failure should become the next held-out task?

## Known limitations to say aloud

- The task suite is small and incident-specific.
- The captured result uses one repetition.
- Model behavior, latency, and token use vary.
- A blind model judge can be biased, unstable, or miscalibrated.
- A separate judge model improves independence but is not ground truth.
- Shadow observation detects removed-boundary failures after execution.
- Simulated in-memory tools are not production services.
- Engineering maintenance cost is discussed, not quantitatively measured.
- Passing known evals does not cover unknown failure modes.

## Final sign-off

| Reviewer | Focus | Status | Notes |
| --- | --- | --- | --- |
| Module instructor | Learning sequence | Pending | |
| Repository maintainer | Code and result alignment | Pending | |
| Evaluation reviewer | Experimental design | Pending | |
| Security reviewer | Safety/authorization claims | Pending | |
| Instructional designer | Timing and cognitive load | Pending | |
| Visual producer | Accessibility and result labeling | Pending | |
