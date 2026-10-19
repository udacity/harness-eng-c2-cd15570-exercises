# Storyboard — Video 2: Skills Are Not Hooks

**Target duration:** 6:15  
**Visual motif:** indigo skill cards, red/green lifecycle gates, solid harness
boundary.

## Slide 1 — Same policy, different guarantees

- **Main message:** Written guidance does not enforce the execution boundary.
- **Minimal on-screen text:** “Advice is not a gate.”
- **Recommended visual:** Safe-remediation text above a rollback call that can
  still reach a tool.
- **Narration segment:** Script 0:00–0:55.
- **Speaker notes:** Ask what physically prevents the wrong target.
- **Animation:** Highlight skipped checklist item, then trace the call forward.
- **Technical accuracy notes:** Do not claim the model always ignores skills.
- **Instructor review:** Approve use of production rollback example.

## Slide 2 — Skill path

- **Main message:** Skills influence model proposals through context.
- **Minimal on-screen text:** “Task match → load guidance → model proposes”
- **Recommended visual:** Model inside a dotted probabilistic boundary reading
  an indigo skill card.
- **Narration segment:** Script 0:55–1:50.
- **Speaker notes:** Name omission, over-selection, misunderstanding, conflict.
- **Animation:** Four risk badges appear around the model.
- **Technical accuracy notes:** Never label skill adherence deterministic.
- **Instructor review:** None.

## Slide 3 — Hook path

- **Main message:** Hooks run at harness-owned lifecycle boundaries.
- **Minimal on-screen text:** “Event → hook → ALLOW or BLOCK”
- **Recommended visual:** Solid gate between proposed tool call and dispatcher;
  trusted state enters from below.
- **Narration segment:** Script 1:50–2:50.
- **Speaker notes:** A hook is not magically safe; wiring and code need tests.
- **Animation:** Send one valid and one invalid target through the gate.
- **Technical accuracy notes:** Use “can be deterministic,” not “all hooks are
  deterministic.”
- **Instructor review:** Verify terminology matches Module 3.

## Slide 4 — Skills plus hooks

- **Main message:** Guidance improves proposals; hooks constrain effects.
- **Minimal on-screen text:** “Better proposal + enforced invariant”
- **Recommended visual:** Skill feeds the model; proposed call enters hook;
  blocked result returns to the model.
- **Narration segment:** Script 2:50–3:45.
- **Speaker notes:** Point out that the loop continues after a block.
- **Animation:** Trace advisory path, then enforcement path, then feedback.
- **Technical accuracy notes:** Hook output is execution evidence; it is not a
  final-response evaluator.
- **Instructor review:** None.

## Slide 5 — Neighboring components

- **Main message:** Tools, permissions, retrieval, hooks, skills, and evaluators
  own distinct responsibilities.
- **Minimal on-screen text:** Six labeled component cards.
- **Recommended visual:** Responsibility matrix with one example per card.
- **Narration segment:** Script 3:45–5:00.
- **Speaker notes:** Spend most time on tool, permission, and evaluator.
- **Animation:** Highlight the component named in each sentence.
- **Technical accuracy notes:** Permissions may be implemented inside a hook
  path, but remain a separate policy responsibility.
- **Instructor review:** Confirm course-wide vocabulary.

## Slide 6 — Placement test

- **Main message:** Four questions identify the correct boundary.
- **Minimal on-screen text:** “Know-how? Event? Identity/data/action? Accept?”
- **Recommended visual:** Decision tree ending in skill, hook, permission/tool,
  or evaluator.
- **Narration segment:** Script 5:00–5:50.
- **Speaker notes:** One rule can have representations at multiple layers.
- **Animation:** Walk the rollback requirement through the tree.
- **Technical accuracy notes:** Avoid treating the tree as exhaustive for every
  architecture.
- **Instructor review:** None.

## Slide 7 — Boundary statement

- **Main message:** Skills never acquire enforcement authority by wording.
- **Minimal on-screen text:** “No authority • no proof • no guarantee”
- **Recommended visual:** Skill card outside a solid security boundary; hook
  and permission gates sit on the boundary.
- **Narration segment:** Script 5:50–6:15.
- **Speaker notes:** Read the full boundary statement from narration.
- **Animation:** Apply “advisory” badge to the skill.
- **Technical accuracy notes:** A skill may reference tools, but execution must
  remain controlled by the harness.
- **Instructor review:** Required sign-off on this slide.
