# Video 4 — Add Skill Loading to the Loop

**Target duration:** 7 minutes  
**Learning objective:** Implement safe discovery, selection, loading, and
conversation continuation with explicit limits and fallback behavior.

## Instructor narration

### [Slide 1] The harness owns loading — 0:00–0:50

The model may propose which skill it wants, but it must not control the
filesystem operation.

The harness owns five stages: discover trusted skills, publish a compact
catalog, receive proposed names, resolve only exact allowlisted entries, and
return the loaded text with provenance.

This is the central loading boundary. A model argument is untrusted input, even
when it looks like a reasonable filename.

### [Slide 2] Discover from a trusted root — 0:50–1:45

In `catalog.py`, discovery scans only immediate `*/SKILL.md` entries beneath a
configured root. It skips symlinked files or parent directories, reads the
frontmatter, and requires a nonempty name and description. The name must match
the folder, and duplicates fail catalog construction.

Production code should also define file-size limits, encoding behavior,
supported metadata, ownership, versioning, and what happens when one package
is invalid. Resolve paths and prove they remain beneath the trusted root.

Discover at startup or deployment time when possible. A bad catalog should be
a visible configuration failure, not a surprise halfway through a sensitive
request.

### [Slide 3] Build metadata-only routing context — 1:45–2:35

`catalog_prompt()` emits one line per skill: name and description. It does not
read bodies into the routing prompt.

The selection instructions tell the model to request every relevant skill and
not write the final answer yet. The harness offers one function interface,
`load_skill`, with one required string argument and no additional properties.

Clear function names, descriptions, and schemas improve model calls, but the
harness still validates every returned item. Schema guidance does not eliminate
malformed or adversarial inputs.

### [Slide 4] Resolve every proposed call — 2:35–3:45

The response may contain zero, one, or many function calls. Iterate over all of
them.

For each call, verify the tool name, parse JSON, require the exact argument
shape, require a string, enforce selection-count and content-size limits, and
look up the string as a catalog key.

Never join the model string onto a path. A request such as `../secret` is simply
an unknown key. It receives a controlled error result correlated to the
original `call_id`.

Decide how to handle duplicates. A simple loop can return an error or dedupe
them while logging the event. Decide whether one invalid call blocks every
valid call or whether results are returned independently. Whatever the policy,
make it explicit and test it.

### [Slide 5] Continue into writing — 3:45–4:45

For each valid request, the harness returns a `function_call_output` with the
matching call ID and complete skill text. In this demo, the second request uses
the selection response ID so the model retains the task and its own selection
context.

The writing call does not offer `load_skill` again. That closes the selection
phase and guarantees this simple design has two serving cycles.

This is a design choice, not a universal rule. More complex agents may allow
later discovery, but then they need cycle limits, repeated-call detection,
context budgets, and a clear termination policy.

### [Slide 6] Handle zero and partial selection — 4:45–5:35

If no skill is requested, the Module 2 path still performs the writing call and
states that no skill was loaded. That behavior lets unrelated tasks succeed and
makes a routing miss observable.

For high-risk tasks, a missing required skill may instead trigger a retry,
human escalation, or failure. Do not silently force a random skill merely to
avoid an empty selection.

If one of several calls fails, return evidence for the failure and preserve the
valid results according to policy. The final output must not claim that an
unknown or rejected skill was loaded.

### [Slide 7] Precedence and conflict — 5:35–6:15

Loaded text is not allowed to override higher-priority base policy, runtime
permissions, or hooks. State that precedence in the writing instructions and
architecture documentation.

When two valid skills conflict, use a documented rule: perhaps a task-specific
skill beats a general style skill, or the harness rejects ambiguous
combinations. Log both versions and the chosen rule. Hidden model improvisation
is not a stable conflict policy.

### [Slide 8] Trace the complete run — 6:15–6:45

Record the catalog version, selection response, requested names, accepted and
rejected calls, source path or package ID, version or content hash, loaded
characters or tokens, both model usages, and both latencies.

Do not log secrets, private chain-of-thought, or unrestricted sensitive file
content. Observability should make the run reproducible without creating a new
data exposure.

### [Slide 9] The complete invariant — 6:45–7:00

The invariant is:

> The model proposes relevance; the harness controls resolution.

Next, we will test whether that mechanism is correct and whether the selected
guidance is actually worth its cost.

## Demonstration cue

Trace `build_selection_instructions()`, `resolve_skill_call()`, and
`write_with_skills()` in `demo/agent.py`. Run the deterministic tests before a
live model comparison.

## Transition line

> Safe loading proves what entered context. Evaluation must still prove what
> changed in behavior.
