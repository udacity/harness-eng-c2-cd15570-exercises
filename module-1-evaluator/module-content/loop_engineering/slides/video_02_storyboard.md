# Storyboard — Video 2: Separate the Generator from the Evaluator

**Target duration:** 6:15  
**Visual motif:** purple generator, orange evaluator, blue controller, gray
evidence cards.

## Slide 1 — One task hides three jobs

- **Main message:** Candidate creation, assessment, and stopping are distinct
  responsibilities.
- **Minimal on-screen text:** “Produce • Assess • Decide”
- **Recommended visual:** A single “agent” box splits into three role cards.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Ask who should own the stop button.
- **Animation:** Split one box into generator, evaluator, controller.
- **Technical accuracy notes:** These are logical responsibilities; they can
  share infrastructure without sharing authority.
- **Instructor review:** Confirm role names align with course terminology.

## Slide 2 — Generator: produce and revise

- **Main message:** The generator owns candidates, not acceptance.
- **Minimal on-screen text:** “Request + context → candidate”
- **Recommended visual:** Purple generator card receiving incident facts and
  emitting Candidate 1, then a dotted revision arrow to Candidate 2.
- **Narration segment:** Script 0:50–1:35.
- **Speaker notes:** Use “candidate” consistently until acceptance.
- **Animation:** Candidate 1 appears; feedback later activates Candidate 2.
- **Technical accuracy notes:** Generator explanations are not authoritative
  execution or acceptance evidence.
- **Instructor review:** None.

## Slide 3 — Evaluator: criterion-level findings

- **Main message:** Evaluation should cite the requirement and conflicting
  evidence.
- **Minimal on-screen text:** “Decision + evidence + feedback”
- **Recommended visual:** Orange evaluator beside a structured JSON finding;
  connect rollback claim to `rollback_performed=false`.
- **Narration segment:** Script 1:35–2:30.
- **Speaker notes:** Read the evidence line aloud; do not read the entire JSON.
- **Animation:** Reveal decision, then evidence, then actionable correction.
- **Technical accuracy notes:** The finding remains a claim to parse and audit;
  it is not automatically ground truth.
- **Instructor review:** Approve JSON complexity for audience level.

## Slide 4 — Controller: accept, retry, or fail

- **Main message:** Operational policy and stopping belong outside model roles.
- **Minimal on-screen text:** “Controller owns the stop rule.”
- **Recommended visual:** Blue controller with four exits: accept, retry,
  escalate, fail; budget gauge above.
- **Narration segment:** Script 2:30–3:25.
- **Speaker notes:** Mention malformed evaluator output as a concrete fail-closed
  case.
- **Animation:** Light exits as their conditions are named.
- **Technical accuracy notes:** Escalation and failure are successful controller
  behaviors when acceptance evidence is missing.
- **Instructor review:** None.

## Slide 5 — Independence is a process property

- **Main message:** Fresh instructions and context create role separation even
  when model names match.
- **Minimal on-screen text:** “Same model can be a separate call.”
- **Recommended visual:** Two API-call cards with the same model label but
  different prompts and no conversation link; a separate-model option sits to
  the side.
- **Narration segment:** Script 3:25–4:30.
- **Speaker notes:** Say “process independence, not statistical independence.”
- **Animation:** First separate contexts, then reveal optional cross-model path.
- **Technical accuracy notes:** Same-family calls can retain correlated
  tendencies. A different model is not automatically less biased.
- **Instructor review:** Verify this nuance remains in final slide notes.

## Slide 6 — Inspiration, not GAN training

- **Main message:** The producer/discriminator analogy is useful; the training
  claim is not.
- **Minimal on-screen text:** “Structural analogy only”
- **Recommended visual:** Small GAN training sketch on the left with a red “not
  this”; inference-time harness roles on the right with a green “this.”
- **Narration segment:** Script 4:30–5:20.
- **Speaker notes:** Avoid a deep GAN explanation. Spend no more than 50 seconds.
- **Animation:** Show shared producer/critic motif, then reveal differences:
  no joint training, no minimax loss, explicit business rubric.
- **Technical accuracy notes:** Cite Goodfellow et al. only as origin of the
  adversarial training analogy.
- **Instructor review:** Optional slide if the audience has no ML background.

## Slide 7 — Self-review versus separated evaluation

- **Main message:** A fresh evaluation boundary creates inspectable evidence.
- **Minimal on-screen text:** Two path diagrams; no prose paragraph.
- **Recommended visual:** Side-by-side flows from the script.
- **Narration segment:** Script 5:20–6:00.
- **Speaker notes:** Point to where shared context ends and controller ownership
  begins.
- **Animation:** Trace self path first, then separated path.
- **Technical accuracy notes:** Do not label the evaluator “objective.” Label it
  “separate” or “independent context.”
- **Instructor review:** Ensure arrows show feedback returning to generator via
  controller.

## Slide 8 — Next: define success

- **Main message:** Separation without measurable criteria produces another
  vague opinion.
- **Minimal on-screen text:** “What exactly must pass?”
- **Recommended visual:** Empty rubric card filling with five criterion slots.
- **Narration segment:** Script 6:00–6:15.
- **Speaker notes:** Transition directly to exact versus inferential checks.
- **Animation:** Reveal question, then blank criterion slots.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
