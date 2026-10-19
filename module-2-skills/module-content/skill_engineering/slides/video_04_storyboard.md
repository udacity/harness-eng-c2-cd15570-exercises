# Storyboard — Video 4: Add Skill Loading to the Loop

**Target duration:** 7:00  
**Visual motif:** blue harness boundary, indigo catalog and skills, numbered
cycle badges.

## Slide 1 — Harness-owned loading

- **Main message:** Model selections are proposals resolved by the harness.
- **Minimal on-screen text:** “Model proposes; harness resolves.”
- **Recommended visual:** Untrusted name crosses into a resolver with a trusted
  catalog behind it.
- **Narration segment:** Script 0:00–0:50.
- **Speaker notes:** Say that model-generated filenames are untrusted input.
- **Animation:** Stop the name at the boundary before any file access.
- **Technical accuracy notes:** None.
- **Instructor review:** None.

## Slide 2 — Trusted discovery

- **Main message:** Validate packages before exposing a catalog.
- **Minimal on-screen text:** “Root • metadata • identity • uniqueness”
- **Recommended visual:** Directory tree passing through validation filters.
- **Narration segment:** Script 0:50–1:45.
- **Speaker notes:** Show the repository's symlink handling.
- **Animation:** Invalid package cards fall out at each filter.
- **Technical accuracy notes:** The demo parser is intentionally minimal and is
  not a general YAML parser.
- **Instructor review:** Security review of path claims.

## Slide 3 — Selection cycle

- **Main message:** Cycle one contains metadata and a narrow loading interface.
- **Minimal on-screen text:** “Cycle 1: select, do not answer”
- **Recommended visual:** Prompt contents: base instructions, task, compact
  catalog, `load_skill` schema.
- **Narration segment:** Script 1:45–2:35.
- **Speaker notes:** Point out that bodies are absent.
- **Animation:** Add four prompt components; keep body cards outside.
- **Technical accuracy notes:** Schema conformance still needs application-side
  validation.
- **Instructor review:** None.

## Slide 4 — Exact resolution

- **Main message:** Parse and validate every call; never turn the name into a
  path.
- **Minimal on-screen text:** “Parse → validate → exact lookup → result”
- **Recommended visual:** Resolver pipeline with known, malformed, traversal,
  and duplicate calls.
- **Narration segment:** Script 2:35–3:45.
- **Speaker notes:** Follow one `../secret` request to an error result.
- **Animation:** Send four call cards through the pipeline.
- **Technical accuracy notes:** Preserve each original `call_id`.
- **Instructor review:** Required security sign-off.

## Slide 5 — Writing cycle

- **Main message:** Return correlated outputs, preserve context, and close the
  loader.
- **Minimal on-screen text:** “Cycle 2: loaded guidance → final output”
- **Recommended visual:** `previous_response_id`, two function outputs, and a
  crossed-out loader feeding the final call.
- **Narration segment:** Script 3:45–4:45.
- **Speaker notes:** This is the demo's fixed two-cycle design.
- **Animation:** Match call IDs, then remove tool icon.
- **Technical accuracy notes:** Provider APIs differ; storyboard matches the
  repository's Responses API path.
- **Instructor review:** Verify API terminology against current official docs.

## Slide 6 — Zero and partial selection

- **Main message:** Empty and mixed results need explicit fallback policy.
- **Minimal on-screen text:** “Zero • valid • rejected • partial”
- **Recommended visual:** Four outcome cards entering policy branches.
- **Narration segment:** Script 4:45–5:35.
- **Speaker notes:** Different risk tiers may choose continue, retry, escalate,
  or fail.
- **Animation:** Reveal each outcome and policy option.
- **Technical accuracy notes:** Do not imply the course's continue behavior is
  right for every production task.
- **Instructor review:** None.

## Slide 7 — Precedence and conflicts

- **Main message:** Loaded guidance cannot override higher-level controls.
- **Minimal on-screen text:** “Policy > task guidance > optional style”
- **Recommended visual:** Layer stack plus collision icon between two skills.
- **Narration segment:** Script 5:35–6:15.
- **Speaker notes:** Avoid claiming one universal provider-independent message
  hierarchy; teach application policy.
- **Animation:** Attempted skill override bounces off policy layer.
- **Technical accuracy notes:** Runtime permissions and hooks remain external.
- **Instructor review:** Approve precedence language.

## Slide 8 — Trace

- **Main message:** Provenance and serving metrics make runs reproducible.
- **Minimal on-screen text:** “Selected • loaded • source • version • size”
- **Recommended visual:** Structured trace with sensitive fields redacted.
- **Narration segment:** Script 6:15–6:45.
- **Speaker notes:** Separate model usage per cycle.
- **Animation:** Populate fields as the run advances.
- **Technical accuracy notes:** Do not log private chain-of-thought or secrets.
- **Instructor review:** Privacy review required.

## Slide 9 — Loading invariant

- **Main message:** Relevance can be probabilistic while resolution remains
  controlled.
- **Minimal on-screen text:** “Propose relevance. Control resolution.”
- **Recommended visual:** Final architecture diagram with solid resolver
  boundary.
- **Narration segment:** Script 6:45–7:00.
- **Speaker notes:** Transition to tests and evaluation.
- **Animation:** Lock icon closes on resolver.
- **Technical accuracy notes:** None.
- **Instructor review:** None.
