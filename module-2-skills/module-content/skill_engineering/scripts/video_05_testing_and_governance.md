# Video 5 — Test, Measure, and Govern Skills

**Target duration:** 6 minutes 15 seconds  
**Learning objective:** Verify the loading boundary, measure behavioral value,
and operate skills as versioned dependencies.

## Instructor narration

### [Slide 1] Two systems need testing — 0:00–0:45

A skill-enabled harness contains two systems: deterministic orchestration and
probabilistic model behavior.

Unit tests can prove that the catalog excludes bodies, traversal is rejected,
call IDs are preserved, and the loader disappears before writing. They cannot
prove the model will select the best skill on every task.

Behavior evaluations can estimate routing and output performance. They cannot
replace exact security and integration tests.

We need both.

### [Slide 2] Test the loading boundary — 0:45–1:45

Begin with deterministic tests that require no API key.

Test valid and malformed frontmatter, duplicate names, folder mismatches,
symlinks, path escape attempts, unknown names, invalid JSON, unexpected
arguments, zero calls, multiple calls, duplicate calls, oversized files, and
selection-count limits.

Assert that the routing prompt contains names and descriptions but not skill
bodies. Assert that the final writing request carries the correct previous
response identifier and does not expose the loader again.

Test failure behavior, not just success. A controlled error returned to the
model is part of the product contract.

### [Slide 3] Evaluate routing separately — 1:45–2:35

Create a representative task set with independently labeled relevant skills.
For each run, compare the selection with those labels.

Precision asks: of the skills loaded, how many were relevant? Recall asks: of
the relevant skills, how many were loaded?

Low precision means extra context and possible conflict. Low recall means
missing expertise. Show raw false-positive and false-negative counts, because a
missed safety procedure may matter more than several harmless extra style
skills.

Include tasks where no skill should load. Otherwise the router can appear
successful by always choosing something.

### [Slide 4] Evaluate the final task — 2:35–3:25

Correct selection is not the end goal. Run eager, on-demand, and when useful
no-skill baselines over the same tasks, model settings, and authoritative data.

Evaluate the finished artifact against the same requirements. For `INC-2048`,
that includes exact word count and incident ID plus independent factual and
usefulness judgments.

Record cases where selection matched but output failed, and where output passed
without the expected skill. Those cases reveal whether the skill is causal,
redundant, weak, or simply correlated with the task label.

Repeat stochastic trials and report variability instead of promoting one good
run into a general claim.

### [Slide 5] Measure the whole serving tradeoff — 3:25–4:20

Measure complete skill characters, input tokens, output tokens, model cycles,
selection latency, writing latency, total serving latency, and cost if verified
pricing is available.

Fewer loaded characters do not guarantee fewer API input tokens. The on-demand
path adds catalog text, a function definition, the selection response, tool
results, and another call.

Report evaluator overhead separately so serving designs remain comparable.
Track fallback and loader errors as first-class metrics. A cheaper path that
silently omits required expertise may be a poor production choice.

### [Slide 6] Govern changes like code — 4:20–5:15

Assign an owner to every skill. Review changes, run deterministic validation,
execute behavior evaluations, and promote through staged environments. Record
a semantic version or immutable content hash in run traces.

Canary a new version on representative traffic. Compare routing and task
outcomes with the previous version. Keep a rollback path. Deprecate skills with
an explicit replacement and remove their catalog entries only after consumers
have migrated.

Review third-party skill packages as supply-chain dependencies. Pin sources,
scan resources, and do not let an update silently expand tool access or add
execution.

### [Slide 7] Diagnose failures by layer — 5:15–5:55

When a skill-enabled run fails, locate the layer.

Was the skill absent from discovery? Was its description ambiguous? Did the
model omit it? Did the loader reject it? Did conflicting content enter context?
Did the model ignore correct guidance? Or did the final evaluator expose a
requirement the skill never addressed?

That trace determines the fix. Lengthening a skill body will not repair a path
validation bug. Forcing selection will not repair stale instructions. Adding a
skill will not repair a missing hook.

### [Slide 8] Production checklist — 5:55–6:15

A production-ready skill path has focused content, discriminative metadata, a
trusted catalog, exact loading, bounded orchestration, explicit precedence,
tests, behavioral evaluation, provenance, and rollback.

And it preserves the boundary from the entire module: skills guide the model;
the harness remains responsible for control.

## Demonstration cue

Run:

```bash
cd module-2-skills/demo
python3 -m unittest discover -s . -p 'test_*.py'
python3 main.py compare --request stakeholder_update
```

Describe observed selections and results. Do not promise a token reduction or
quality win.

## Closing line

> A useful skill is not merely a good prompt file. It is a governed dependency
> inside a tested loading and evaluation system.
