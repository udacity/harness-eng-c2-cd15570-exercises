# Storyboard — Video 3: Author Skills That Route Well

**Target duration:** 6:30  
**Visual motif:** a two-sided skill card—metadata on the front, instructions on
the back.

## Slide 1 — Two audiences

- **Main message:** Metadata supports selection; the body supports execution.
- **Minimal on-screen text:** “Should I load it? How should I work?”
- **Recommended visual:** Flip card with catalog-facing and model-facing sides.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Keep “execution” here as task performance, not side effects.
- **Animation:** Flip from metadata to instructions.
- **Technical accuracy notes:** Clarify that the same model may participate in
  both decisions in separate cycles.
- **Instructor review:** None.

## Slide 2 — Routable metadata

- **Main message:** Descriptions must identify both capability and trigger.
- **Minimal on-screen text:** “What it does + when to use it”
- **Recommended visual:** Bad description and improved description side by side.
- **Narration segment:** Script 0:50–1:50.
- **Speaker notes:** Read only the improved description aloud.
- **Animation:** Strike “helps with incidents”; reveal discriminative phrases.
- **Technical accuracy notes:** Repository parser also requires folder/name
  match.
- **Instructor review:** Approve naming convention explanation.

## Slide 3 — Actionable body

- **Main message:** Organize instructions around decisions and evidence.
- **Minimal on-screen text:** “Purpose • inputs • workflow • edges • output”
- **Recommended visual:** Annotated `SKILL.md` wireframe.
- **Narration segment:** Script 1:50–2:55.
- **Speaker notes:** Contrast “be accurate” with a concrete prohibition.
- **Animation:** Reveal sections from highest to lowest priority.
- **Technical accuracy notes:** Examples must not become runtime facts.
- **Instructor review:** None.

## Slide 4 — Scope and composition

- **Main message:** Skills should compose without becoming fragments or
  monoliths.
- **Minimal on-screen text:** “One coherent capability”
- **Recommended visual:** Giant skill breaks into four useful cards; an
  over-fragmented row recombines into two cards.
- **Narration segment:** Script 2:55–3:45.
- **Speaker notes:** Explain the tradeoff rather than prescribe a line count.
- **Animation:** Split monolith, then merge fragments.
- **Technical accuracy notes:** Composition requires conflict policy.
- **Instructor review:** None.

## Slide 5 — Stable method, fresh state

- **Main message:** Skills hold procedures; retrieval supplies changing facts.
- **Minimal on-screen text:** “Skill: how • Tool: now”
- **Recommended visual:** Runbook procedure beside a live incident-state card.
- **Narration segment:** Script 3:45–4:35.
- **Speaker notes:** Use current deployment as the volatile-fact example.
- **Animation:** Move `checkout-v42` out of the skill into runtime data.
- **Technical accuracy notes:** Some stable reference data may be packaged with
  skills, but freshness requirements must be explicit.
- **Instructor review:** None.

## Slide 6 — Broader spec versus course profile

- **Main message:** Support and conformance must be stated precisely.
- **Minimal on-screen text:** “Open format ≠ this exact implementation”
- **Recommended visual:** Venn diagram: broader skill directory format and
  course subset.
- **Narration segment:** Script 4:35–5:20.
- **Speaker notes:** Mention underscore versus hyphen naming without dwelling.
- **Animation:** Broader features fade; course-supported features stay bright.
- **Technical accuracy notes:** Recheck the cited specification before final
  recording because it can evolve.
- **Instructor review:** Required technical review.

## Slide 7 — Trust and ownership

- **Main message:** Skill packages are governed dependencies.
- **Minimal on-screen text:** “Review • pin • trace • roll back”
- **Recommended visual:** Supply-chain pipeline from author to registry to
  harness, with review and hash badges.
- **Narration segment:** Script 5:20–6:10.
- **Speaker notes:** State that reading a skill must not execute scripts.
- **Animation:** Add gates for review, signing/hash, sandboxed execution.
- **Technical accuracy notes:** A hash proves identity/integrity relative to a
  known value, not that content is safe.
- **Instructor review:** Security review required.

## Slide 8 — Authoring review

- **Main message:** Route, use, trace, and enforce at the correct layer.
- **Minimal on-screen text:** Four-item readiness checklist.
- **Recommended visual:** Skill card passes four review stamps.
- **Narration segment:** Script 6:10–6:30.
- **Speaker notes:** Transition to loader mechanics.
- **Animation:** Stamp each check.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
