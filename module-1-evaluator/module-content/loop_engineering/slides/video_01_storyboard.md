# Storyboard — Video 1: When Agents Judge Their Own Work

**Target duration:** 6:00  
**Visual motif:** one purple model card initially occupies both “author” and
“judge” positions; red evidence markers reveal the conflict.

## Slide 1 — A polished failure

- **Main message:** Fluent and confident output can violate explicit facts and
  format requirements.
- **Minimal on-screen text:** “Looks finished. Is it correct?”
- **Recommended visual:** Incident snapshot on the left; flawed stakeholder
  update on the right. Highlight “resolved,” “rolled back,” and “normal” in red.
- **Narration segment:** Script 0:00–0:55, ending with the incorrect structured
  `VERDICT: PASS`.
- **Speaker notes:** Tell the audience that the candidate and self-review are
  deliberately scripted illustrations. Pause before revealing the incident
  contradictions.
- **Animation:** Reveal the update first, then the authoritative `false` fields,
  then stamp the self-review with “unsupported pass.”
- **Technical accuracy notes:** Ticket says `DEGRADED`, 18% error rate, no
  rollback, and no confirmed recovery. Do not imply this exact false positive
  occurs in every live run.
- **Instructor review:** Confirm whether to show the full bad update or a
  shortened excerpt for readability.

## Slide 2 — Apparent success is not requirement satisfaction

- **Main message:** Execution and confidence are observations; acceptance
  requires criterion-level evidence.
- **Minimal on-screen text:** “Response exists ≠ requirements pass”
- **Recommended visual:** Two-column checklist: “Apparent” has response,
  grammar, confidence; “Verified” has word count, ID, grounding, next step.
- **Narration segment:** Script 0:55–1:45.
- **Speaker notes:** Ask learners which criteria they can verify without an LLM.
- **Animation:** Check apparent signals in gray, then verified signals in green
  only as evidence appears.
- **Technical accuracy notes:** `split()` is the course's declared word-count
  rule; acknowledge that other products may define tokenization differently.
- **Instructor review:** Approve the term “apparent success.”

## Slide 3 — The yes-agent trap

- **Main message:** A broad self-review can reuse the generator's framing and
  blind spots.
- **Minimal on-screen text:** “Familiarity is not evidence.”
- **Recommended visual:** One conversation bubble loops from generator output
  back into the same model, with shared context shaded purple.
- **Narration segment:** Script 1:45–2:45.
- **Speaker notes:** Preserve the balanced wording: self-review can help; it is
  weak as the sole acceptance authority.
- **Animation:** Show author role, expand the same bubble into judge role, then
  overlay “shared assumptions.”
- **Technical accuracy notes:** Discuss correlated context, not a claim that
  models possess human pride or intention.
- **Instructor review:** Confirm “yes-agent” tone fits the course voice.

## Slide 4 — Premature exit

- **Main message:** Passing one operational signal does not prove the task is
  complete.
- **Minimal on-screen text:** “Ran successfully” ≠ “task succeeded”
- **Recommended visual:** Four small cards: syntax/no correct result; files/no
  feature; grammar/no support; incident ID/invented rollback.
- **Narration segment:** Script 2:45–3:45.
- **Speaker notes:** Connect to the demo's basic loop: two generations, no
  quality judgment.
- **Animation:** Each card first shows a green execution check, then a red task
  failure.
- **Technical accuracy notes:** Avoid suggesting syntax checks are unimportant;
  they are necessary but incomplete.
- **Instructor review:** Select two examples if timing is tight.

## Slide 5 — Vibe acceptance compounds errors

- **Main message:** Weak stopping rules allow approximately correct outputs to
  become future inputs.
- **Minimal on-screen text:** “Looks okay → reused → amplified”
- **Recommended visual:** Conveyor belt where a small unsupported claim is
  copied into a template, cached answer, and downstream agent context.
- **Narration segment:** Script 3:45–4:45.
- **Speaker notes:** Introduce the IKEA effect only as an analogy and explicitly
  disclaim universal model psychology.
- **Animation:** The red error marker grows as it moves downstream.
- **Technical accuracy notes:** “Normalization of deviance” describes process
  drift here; do not present it as a measured property of this demo.
- **Instructor review:** Decide whether the IKEA analogy helps or distracts.

## Slide 6 — Change the stop rule

- **Main message:** Acceptance authority belongs in the harness.
- **Minimal on-screen text:** “Generate. Verify. Then stop.”
- **Recommended visual:** Morph the self-loop into generator → exact checks +
  evaluator → controller.
- **Narration segment:** Script 4:45–5:40.
- **Speaker notes:** Emphasize that “think harder” is not the architectural
  change.
- **Animation:** Break the single purple loop; move the stop sign from the model
  to a blue controller.
- **Technical accuracy notes:** The controller combines evidence; it does not
  make semantic judgments without a check.
- **Instructor review:** This visual should establish colors reused in Video 2.

## Slide 7 — Next: three responsibilities

- **Main message:** Generator, evaluator, and controller need distinct jobs.
- **Minimal on-screen text:** “Author • Critic • Controller”
- **Recommended visual:** Three labeled cards with one-line responsibilities.
- **Narration segment:** Script 5:40–6:00.
- **Speaker notes:** End on curiosity, not fear of models.
- **Animation:** Reveal the three cards left to right.
- **Technical accuracy notes:** “Independent” will be defined as context and
  responsibility separation in the next video.
- **Instructor review:** None.
