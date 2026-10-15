# Storyboard — Video 4: Engineer the Evaluation Loop

**Target duration:** 7:00  
**Visual motif:** a bounded circular path with visible attempt and budget meters.

## Slide 1 — Evidence-driven control loop

- **Main message:** Repetition adds value only when each cycle responds to
  evidence.
- **Minimal on-screen text:** “Generate → evaluate → revise → re-evaluate”
- **Recommended visual:** Four-stage loop with a separate accept/fail exit.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Contrast a loop with a fixed rewrite sequence.
- **Animation:** Draw arrows one at a time; reveal exit last.
- **Technical accuracy notes:** Acceptance and failure are terminal states;
  revision is not guaranteed.
- **Instructor review:** None.

## Slide 2 — Keep conversation branches separate

- **Main message:** Generator continuity and evaluator freshness serve different
  purposes.
- **Minimal on-screen text:** Response-ID table from the script.
- **Recommended visual:** Purple generator branch and orange evaluator branch;
  evaluator has no incoming conversation-history arrow.
- **Narration segment:** Script 0:50–1:50.
- **Speaker notes:** Tie directly to Module 1 Responses API output.
- **Animation:** Candidate branch persists; evaluator branch starts fresh; only
  findings cross back through controller.
- **Technical accuracy notes:** A fresh call still receives supplied task
  evidence; fresh does not mean context-free.
- **Instructor review:** Confirm terminology matches SDK used in recording.

## Slide 3 — Structured findings

- **Main message:** The controller needs parseable, criterion-level evidence.
- **Minimal on-screen text:** “passed • evidence • feedback”
- **Recommended visual:** JSON result with three fields highlighted.
- **Narration segment:** Script 1:50–2:45.
- **Speaker notes:** Read only the failed grounding item.
- **Animation:** Highlight schema validation; malformed result takes a red fail
  path.
- **Technical accuracy notes:** Machine-readable output reduces ambiguity but
  does not guarantee factual correctness.
- **Instructor review:** Approve JSON versus line-oriented format.

## Slide 4 — Controller pseudocode

- **Main message:** One compact controller can own evidence, revision, and stop
  rules.
- **Minimal on-screen text:** The core 12-line loop.
- **Recommended visual:** Code on left; state diagram on right.
- **Narration segment:** Script 2:45–3:50.
- **Speaker notes:** Highlight same candidate, actionable feedback, and
  re-evaluation.
- **Animation:** Step through attempt 1; do not type code live.
- **Technical accuracy notes:** Production code also needs exception handling,
  cancellation, persistence, and privacy controls.
- **Instructor review:** None.

## Slide 5 — Bound every resource

- **Main message:** Attempts, tokens, money, and time are controller policy.
- **Minimal on-screen text:** “Attempts • tokens • cost • latency”
- **Recommended visual:** Four gauges surrounding the loop; threshold line on
  each.
- **Narration segment:** Script 3:50–4:45.
- **Speaker notes:** Say “a maximum is not a success condition.”
- **Animation:** Each gauge reaches its bound; loop exits to failure.
- **Technical accuracy notes:** Quality thresholds must not replace hard safety
  criteria when any single failure is disqualifying.
- **Instructor review:** None.

## Slide 6 — Maximum retries can end in failure

- **Main message:** Exhausted retries must preserve unresolved criteria.
- **Minimal on-screen text:** “Attempt 3: grounding still FAIL → escalate”
- **Recommended visual:** Three candidate cards; fixed checks turn green, but
  grounding remains red on attempts 2 and 3.
- **Narration segment:** Script 4:45–5:40.
- **Speaker notes:** Read the terminal record. Do not show the last candidate as
  an accepted output.
- **Animation:** Advance attempts; final arrow goes to red FAILED state.
- **Technical accuracy notes:** The controller may return a marked draft, but
  `accepted` remains false.
- **Instructor review:** This is a required teaching moment; do not cut.

## Slide 7 — Logs show progress and regression

- **Main message:** Criterion history reveals whether revision actually helped.
- **Minimal on-screen text:** “resolved • persisted • regressed”
- **Recommended visual:** Attempt-by-criterion heatmap with one criterion
  turning green and another newly red.
- **Narration segment:** Script 5:40–6:30.
- **Speaker notes:** Mention privacy: retain decisions and evidence, not private
  chain-of-thought.
- **Animation:** Transition cells across attempts.
- **Technical accuracy notes:** Model and prompt versions are required for
  reproducibility.
- **Instructor review:** Approve retention/privacy language.

## Slide 8 — Escalation is a valid terminal state

- **Main message:** Human review is safer than automatic acceptance without
  evidence.
- **Minimal on-screen text:** “Unresolved ≠ accepted”
- **Recommended visual:** Controller routes a high-risk failed case to a human
  review queue.
- **Narration segment:** Script 6:30–6:50.
- **Speaker notes:** Give one trigger: repeated grounding failure.
- **Animation:** Red case exits loop and enters review queue.
- **Technical accuracy notes:** Human review also needs a rubric and evidence.
- **Instructor review:** None.

## Slide 9 — Next: measure value

- **Main message:** A correctly engineered evaluator still must earn its cost.
- **Minimal on-screen text:** “Better outcomes per unit cost?”
- **Recommended visual:** Balance scale with quality evidence and operational
  overhead.
- **Narration segment:** Script 6:50–7:00.
- **Speaker notes:** None.
- **Animation:** Balance settles unresolved to lead into Video 5.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
