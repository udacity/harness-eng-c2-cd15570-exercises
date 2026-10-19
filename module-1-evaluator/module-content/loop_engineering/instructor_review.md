# Instructor Review Packet

## Review status

This package is a complete first draft for technical and instructional review.
It is not a final recording script or finished slide deck.

## Decisions required before recording

### 1. Runtime and exercise emphasis

- [ ] Confirm that the first hands-on exercise emphasizes inferential
  separation before students implement every deterministic check.
- [ ] Confirm that the video still introduces deterministic checks as the
  target production design.
- [ ] Confirm whether the customer-support exercise or `INC-2048` demo should
  appear in the final recap.

### 2. Terminology

- [ ] Approve “generator,” “self-evaluator,” “independent evaluator,” and
  “harness controller.”
- [ ] Approve “false acceptance” and “false rejection” instead of the more
  classification-oriented “false positive” and “false negative.”
- [ ] Confirm that “process independence, not statistical independence” is
  accessible to the audience.
- [ ] Decide whether “yes-agent trap” and “vibe acceptance” fit the course tone.

### 3. Demonstration strategy

- [ ] Approve the scripted false-positive example for a guaranteed opening.
- [ ] Keep a visible `SCRIPTED ILLUSTRATION` label on that example.
- [ ] For live demonstrations, commit to narrating the observed result rather
  than promising self-review disagreement.
- [ ] Confirm the exact word-count convention: Python whitespace `split()`.
- [ ] Decide whether to run all three Module 1 loop modes during video or use
  captured output for pacing.

### 4. Acceptance policy

- [ ] Approve all-required-criteria pass semantics.
- [ ] Confirm whether response shape is a required third deterministic
  criterion or only an extension beyond the current demo.
- [ ] Approve fail-closed behavior for malformed evaluator output.
- [ ] Approve maximum-attempt terminal status as `FAILED`, never accepted.
- [ ] Identify tasks that require human escalation rather than another retry.

### 5. Measurement example

- [ ] Approve the synthetic 20-case confusion matrices for teaching formulas.
- [ ] Confirm the permanent “ILLUSTRATIVE — NOT BENCHMARK DATA” watermark.
- [ ] Decide whether quality-gain-per-token is useful for this audience or
  belongs only in instructor notes.
- [ ] Confirm that real studies must report repetitions and variability.

## Technical accuracy checklist

- [ ] Self-review is described as fallible, not universally ineffective.
- [ ] Independent LLM evaluation is described as fallible, not objective.
- [ ] Separate model choice is optional and experimentally evaluated.
- [ ] Deterministic checks are preferred for computable properties.
- [ ] Evaluator outputs contain criterion decisions, evidence, and feedback.
- [ ] The controller—not a model—owns accept, retry, fail, and escalation.
- [ ] Every revision is re-evaluated.
- [ ] Attempt and budget exhaustion produce failure, not success.
- [ ] Logs exclude secrets and private chain-of-thought.
- [ ] GAN language is explicitly limited to structural inspiration.
- [ ] IKEA effect is explicitly identified as a human analogy.

## Storyboard review checklist

- [ ] Each slide has one primary message.
- [ ] Slides do not repeat the full narration as text.
- [ ] Generator, evaluator, controller, evidence, and checks use consistent
  colors and shapes.
- [ ] Pass/fail uses icons and labels in addition to color.
- [ ] Every data chart includes counts, denominators, and data provenance.
- [ ] All code is readable at 1080p.
- [ ] Animations show causal order rather than decorative motion.
- [ ] Alt text is transferred into final slide assets.

## Suggested live-demo checkpoints

### Basic loop

Ask:

> What evidence says the second response is better?

Expected discussion: the loop requested a clearer rewrite but performed no
evaluation. More cycles do not prove quality.

### Self-evaluation loop

Ask:

> Which part of this verdict is independent of the generator conversation?

Expected discussion: none. The output may still be helpful feedback, but the
same conversation supplies the stopping signal.

### External evaluation loop

Ask:

> Which criteria are calculated by code, and which require judgment?

Expected discussion: exact word count and incident ID are deterministic;
factual grounding and usefulness are inferential.

If no false positive appears, say:

> In this run, self-review and independent review agree. The architecture still
> matters because the external decision is supported by evidence outside the
> generator conversation.

If the attempt limit is reached, say:

> The harness stopped without acceptance. That is correct behavior: the limit
> bounds cost, while the unresolved evidence preserves the failure.

## Research review questions

1. Are R1 and R2 presented together clearly enough to avoid cherry-picking a
   simple “self-review works/does not work” conclusion?
2. Should Video 5 include the specific LLM-judge bias names, or keep them in
   notes for an advanced audience?
3. Is CriticGPT sufficiently close to this course's evaluation use case to
   mention in narration, or should it remain a reference only?
4. Does the GAN analogy add value proportional to the clarification it needs?
5. Should the IKEA analogy be retained, moved to notes, or removed?

## Production checklist

- [ ] Resolve every unchecked decision above.
- [ ] Copy approved script wording into the teleprompter format.
- [ ] Produce diagrams from editable sources.
- [ ] Run the live demo with the recording model and save output.
- [ ] Replace any illustrative live-output screenshot with the actual captured
  run and label it with model/date.
- [ ] Verify all citations and third-party asset records.
- [ ] Perform technical review of code and metric formulas.
- [ ] Perform accessibility review.
- [ ] Time a complete read at a natural pace; trim to 25–35 minutes.
- [ ] Record only after content, legal/asset, and exercise-alignment approval.

## Recommended acceptance criteria for this collateral

The package is ready for slide production when:

- all five learning objectives have matching narration and storyboard coverage;
- scripts total 25–35 minutes in a timed read;
- every empirical claim is cited or labeled illustrative;
- examples align with the repository's Module 1 behavior;
- the instructor approves terminology and demonstration contingencies; and
- no unresolved technical-accuracy item remains.
