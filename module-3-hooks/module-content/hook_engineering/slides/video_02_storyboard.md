# Storyboard — Video 2: Place Hooks in the Lifecycle

**Target duration:** 6:15  
**Visual motif:** numbered lifecycle states and a solid stop gate before the
business tool.

## Slide 1 — Proposal is not execution

- **Main message:** Model output requests an action; application evidence proves
  execution.
- **Minimal on-screen text:** “Requested ≠ executed”
- **Recommended visual:** Tool-call card suspended before an execution line.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Read the state verbs: requested, parsed, authorized,
  allowed, executed, verified.
- **Animation:** Add evidence badge at each transition.
- **Technical accuracy notes:** A function call item is not tool completion.
- **Instructor review:** None.

## Slide 2 — Before-tool sequence

- **Main message:** Parse, resolve, authorize, validate, then dispatch.
- **Minimal on-screen text:** Five numbered steps.
- **Recommended visual:** Pipeline with block exits before dispatch.
- **Narration segment:** Script 0:50–1:50.
- **Speaker notes:** Permission is previewed but not implemented in Module 3.
- **Animation:** Trace valid and invalid calls.
- **Technical accuracy notes:** Keep authorization and validity distinct.
- **Instructor review:** Confirm transition to Module 4.

## Slide 3 — Policy-light tool

- **Main message:** The same business tool executes only after external policy
  decisions pass.
- **Minimal on-screen text:** “Tool performs; boundary decides.”
- **Recommended visual:** One permissive tool shared by basic and hook paths.
- **Narration segment:** Script 1:50–2:40.
- **Speaker notes:** Mention low-level validation and database constraints as
  defense in depth.
- **Animation:** Basic path bypasses gate; hook path enters gate.
- **Technical accuracy notes:** Do not recommend removing all validation from
  real tools.
- **Instructor review:** None.

## Slide 4 — Block result returns

- **Main message:** Blocking prevents dispatch while preserving loop feedback.
- **Minimal on-screen text:** “BLOCK → no tool → structured result”
- **Recommended visual:** Red block card loops back to model with matching
  `call_id`.
- **Narration segment:** Script 2:40–3:30.
- **Speaker notes:** A block is a handled outcome, not a crash.
- **Animation:** Stop tool arrow, then move violations back to model.
- **Technical accuracy notes:** Result must not falsely use the tool's success
  status.
- **Instructor review:** None.

## Slide 5 — Hook map

- **Main message:** Different lifecycle events support different controls.
- **Minimal on-screen text:** “Pre-model • pre-tool • post-tool • pre-complete • cycle”
- **Recommended visual:** One loop with named attachment points.
- **Narration segment:** Script 3:30–4:25.
- **Speaker notes:** Highlight pre-tool only as Module 3 implementation.
- **Animation:** Pin hook icons at lifecycle events.
- **Technical accuracy notes:** Post-execution checks cannot guarantee
  prevention unless the operation is reversible/transactional.
- **Instructor review:** None.

## Slide 6 — Decision ordering

- **Main message:** Authorization, validity, execution, and evaluation answer
  different questions.
- **Minimal on-screen text:** “May they? Is it valid? Did it run? Was it good?”
- **Recommended visual:** Four labeled gates/cards in order.
- **Narration segment:** Script 4:25–5:20.
- **Speaker notes:** Use authorized-but-invalid and valid-but-unauthorized pairs.
- **Animation:** Show both calls stopping at different gates.
- **Technical accuracy notes:** Module 3 does not yet enforce role policy.
- **Instructor review:** Required course-sequence review.

## Slide 7 — Coverage map

- **Main message:** A hook protects only paths routed through it.
- **Minimal on-screen text:** “Every route to the effect”
- **Recommended visual:** Dispatcher hub with API, worker, job, and admin routes;
  one attempted bypass in red.
- **Narration segment:** Script 5:20–5:55.
- **Speaker notes:** Centralize or enforce at the data boundary.
- **Animation:** Trace all routes through hook; expose bypass.
- **Technical accuracy notes:** None.
- **Instructor review:** Security review.

## Slide 8 — Hook and antidote

- **Main message:** Hook is the event; antidote is the exact rule.
- **Minimal on-screen text:** “Control point + predicate”
- **Recommended visual:** Empty hook socket receives five antidote modules.
- **Narration segment:** Script 5:55–6:15.
- **Speaker notes:** Transition directly.
- **Animation:** Insert modules.
- **Technical accuracy notes:** “Antidote” is course terminology.
- **Instructor review:** None.
