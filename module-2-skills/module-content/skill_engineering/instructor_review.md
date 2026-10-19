# Instructor Review Packet

## Review status

This package is a complete first draft for technical, instructional, security,
and production review. It is not a finished slide deck or recorded lesson.

## Decisions required before recording

### 1. Terminology and scope

- [ ] Approve “skill” as reusable model-facing guidance.
- [ ] Approve “hook” as harness code attached to a lifecycle event.
- [ ] Preserve the sentence: “Skills guide model behavior; hooks enforce
  application behavior.”
- [ ] Confirm “activation,” “selection,” and “loading” usage.
- [ ] Decide whether to name the capability/exercise IDs once course mapping is
  final.

### 2. Specification framing

- [ ] Confirm that the course demo is labeled a local, simplified skill
  profile rather than fully specification-conformant.
- [ ] Recheck current Agent Skills naming and metadata constraints.
- [ ] Approve the underscore-versus-hyphen compatibility note.
- [ ] Confirm whether optional `scripts/`, `references/`, and `assets/` belong in
  narration or speaker notes only.

### 3. Skills-versus-hooks boundary

- [ ] A skill never grants authorization.
- [ ] A skill never proves current state.
- [ ] A skill never guarantees model compliance.
- [ ] A mandatory hook runs because the harness reaches the event, not because
  the model selects it.
- [ ] The remediation example shows both layers as complementary.
- [ ] Module 2 does not pre-teach all Module 3 implementation details.

### 4. Loader architecture

- [ ] The catalog contains metadata only.
- [ ] Model-supplied names are never interpreted as paths.
- [ ] Every call is parsed, schema-checked, allowlisted, and correlated.
- [ ] Zero, multiple, duplicate, malformed, unknown, and oversized requests
  have explicit behavior.
- [ ] The writing cycle removes the loading tool in the course implementation.
- [ ] Cycle, count, size, token, and latency limits are described as configurable
  policy rather than universal constants.

### 5. Security and governance

- [ ] Skill content is treated as a reviewed dependency and prompt-injection
  surface.
- [ ] No skill text contains credentials or real private endpoints.
- [ ] Reading a skill never implies executing its scripts.
- [ ] Provenance includes owner/source and version or immutable hash.
- [ ] Hashing is not described as proof of safety.
- [ ] Rollout, monitoring, rollback, and deprecation are included.

### 6. Measurement

- [ ] Routing precision and recall formulas are correct.
- [ ] No-skill tasks are included in behavior evaluations.
- [ ] Final task success is measured independently of routing match.
- [ ] Both serving cycles contribute to tokens and latency.
- [ ] Evaluator overhead remains separate.
- [ ] Every sample number is visibly labeled illustrative.
- [ ] Live results are narrated as observations, not guaranteed outcomes.

## Technical accuracy checklist

- [ ] `catalog.py` behavior is described exactly.
- [ ] The local parser is not described as a full YAML implementation.
- [ ] The demo tool schema includes one required string and rejects extra
  properties, but does not set the provider `strict: true` flag.
- [ ] The production pseudocode recommends `strict: true` while retaining
  application-side validation.
- [ ] The response may contain zero, one, or multiple function calls.
- [ ] Tool outputs preserve the original `call_id`.
- [ ] `previous_response_id` is used only where the repository uses it.
- [ ] The loader is absent from the final writing call.
- [ ] The no-skill case continues in the demo.
- [ ] Loading a skill is not described as executing a production action.
- [ ] Selection match is not described as final acceptance.
- [ ] Fewer skill characters are not equated with fewer total tokens.

## Storyboard review checklist

- [ ] Every slide has one primary message.
- [ ] Dotted arrows consistently mean model influence.
- [ ] Solid gates consistently mean harness control.
- [ ] Skill and hook colors are distinguishable without relying on color alone.
- [ ] Catalog visuals contain no complete body text.
- [ ] Every malformed call stops at the resolver boundary.
- [ ] Course-profile and broader-format visuals are clearly labeled.
- [ ] Charts show denominators, provenance, and illustrative watermark.
- [ ] Code is readable at 1080p and contains no secrets.
- [ ] Alt text is transferred into final assets.

## Suggested live-demo checkpoints

### Skill anatomy

Ask:

> Which lines help the router choose this skill, and which lines help the model
> perform the task?

Expected discussion: frontmatter name/description support routing; the body
contains detailed procedure and constraints.

### Eager baseline

Ask:

> Which complete skills entered context even though this is only a stakeholder
> update?

Expected discussion: all four enter the eager prompt.

### On-demand selection

Ask:

> What does the loader prove, and what does it not prove?

Expected discussion: it proves which allowlisted text was returned; it does not
prove correct adherence or final quality.

### Skills versus hooks

Ask:

> If the safe-remediation skill says not to use an unsafe target, what prevents
> the tool from executing if the model requests one anyway?

Expected discussion: a correctly wired before-tool hook or equivalent
deterministic execution boundary, not the skill text.

### Comparison table

Ask:

> Did selective loading reduce complete skill text? Did it reduce total tokens,
> latency, and errors as well?

Expected discussion: each measure must be read separately from the observed
run.

## Demonstration contingencies

If the model selects the expected skill:

> The observed selection matches the teaching label. We still evaluate the
> final note separately.

If it selects an extra skill:

> This is a routing false positive for our label set. The harness loads only an
> allowlisted file, but irrelevant context still has a cost.

If it omits a relevant skill:

> This is a routing false negative. The fallback lets the run complete, so we
> can observe whether the output also fails.

If it selects no skill:

> The demo's explicit fallback proceeds without detailed skill guidance. A
> higher-risk system could retry, escalate, or fail instead.

If on-demand uses more tokens or time:

> The extra selection call is part of the serving design. Progressive
> disclosure is an architectural tradeoff, not a guaranteed cost reduction.

## Production checklist

- [ ] Resolve all decisions above.
- [ ] Recheck external specification and official OpenAI documentation.
- [ ] Run the deterministic Module 2 tests.
- [ ] Capture a live run with model identifier and date.
- [ ] Replace illustrative terminal visuals with the captured run.
- [ ] Verify every external citation and asset record.
- [ ] Perform security review of loader claims and examples.
- [ ] Perform accessibility review.
- [ ] Time a complete read at a natural pace; keep total between 25 and 35
  minutes.
- [ ] Record only after technical and course-alignment approval.

## Recommended acceptance criteria

The package is ready for slide production when:

- every learning objective maps to narration and storyboard coverage;
- the skills-versus-hooks boundary is accurate and repeated consistently;
- the loader sequence covers all stated failure cases;
- examples align with Module 2 repository behavior;
- external-format differences are clearly disclosed;
- empirical claims are sourced or labeled illustrative; and
- no security, technical-accuracy, or terminology item remains unresolved.
