# Video 3 — Author Skills That Route Well

**Target duration:** 6 minutes 30 seconds  
**Learning objective:** Create a focused skill contract whose metadata supports
routing and whose body supports correct task execution.

## Instructor narration

### [Slide 1] A skill has two audiences — 0:00–0:50

A skill file serves two different decisions.

The first decision is whether to load it. That decision needs compact,
discriminative metadata. The second decision is how to perform the task. That
needs detailed instructions.

If the description is vague, the router cannot choose reliably. If the body is
vague, correct routing still produces weak behavior. Good skill engineering
designs both interfaces deliberately.

### [Slide 2] Name and description — 0:50–1:50

In the Module 2 repository, each skill directory contains `SKILL.md` with YAML
frontmatter. The parser requires `name` and `description`, and the name must
match the parent directory.

The name should be stable and specific. The description should say what the
skill does and when to use it. “Helps with incidents” overlaps everything.
“Use when writing an internal or stakeholder incident update, especially when
recovery is not yet confirmed” provides routing signals and a boundary.

Descriptions should not contain the complete procedure. Every description is
always present in the selection prompt, so catalog length grows with the number
of skills.

Compare descriptions together. Routing is a catalog-level property, not just a
file-level property.

### [Slide 3] Structure the body for action — 1:50–2:55

Begin the body with purpose and scope. Then state required inputs, a concrete
workflow, evidence boundaries, edge cases, and the output contract.

Put the highest-value instructions early. Use direct verbs. Separate what the
model must preserve from optional style advice. Explain meaningful states such
as proposed, authorized, executed, effective, recovered, and resolved.

Examples can clarify difficult distinctions, but examples are not facts for
the next request. Avoid long collections of nearly identical samples that
consume context without adding a decision rule.

Write what not to do when the error is plausible and consequential. “Do not
invent a recovery time” is more testable than “be accurate.”

### [Slide 4] Keep the responsibility narrow — 2:55–3:45

A skill should represent one coherent capability. A giant “incident response”
skill containing diagnostics, remediation, communications, permissions, and
every service runbook is difficult to route and difficult to update.

Split skills when parts activate for meaningfully different task families.
Compose them when one request legitimately needs several capabilities.

Do not split so finely that every task needs ten fragments with hidden ordering
dependencies. The useful unit is one independently understandable procedure,
not one paragraph.

If two skills often conflict, clarify their scopes, define precedence in the
harness or base instructions, and add a conflict test. Do not expect the model
to invent a stable precedence policy.

### [Slide 5] Stable guidance, current data — 3:45–4:35

Skills should contain stable methods. Current prices, incident status, account
roles, inventory, and deployment health belong in authoritative stores or
retrieval tools.

The checkout runbook can say which health and log dimensions to inspect. It
should not say that `checkout-v42` is always the current deployment. That is a
fact for this incident snapshot.

This split improves freshness and security. It also makes the skill reusable
across cases without silently carrying yesterday's state into today's task.

### [Slide 6] Specification and local profile — 4:35–5:20

The open Agent Skills specification describes a directory centered on
`SKILL.md`, with required metadata and optional scripts, references, and
assets. It recommends progressive disclosure across metadata, instructions,
and resources.

This course demo uses a smaller local profile. It supports one Markdown file,
reads only two metadata fields, uses underscore names, and does not recursively
load resources. The broader specification currently uses hyphenated naming
constraints, so these course skills should not be labeled fully conformant.

Always document the exact profile your harness supports. Portability requires
validation against the target runtime, not just a familiar filename.

### [Slide 7] Trust and ownership — 5:20–6:10

Treat skill content as a software dependency. Record an owner and source,
review changes, pin a version or content hash for reproducibility, and define a
rollback path.

Never place credentials in a skill. Review links, scripts, and referenced
content before making them available. A malicious or compromised skill can
attempt to override higher-priority instructions or induce unsafe tool use.
Prompt text is not a security boundary.

If executable resources are supported, their execution must go through an
explicit, permissioned, sandboxed tool path. Reading a skill must not silently
execute its contents.

### [Slide 8] Authoring review — 6:10–6:30

Before publishing, ask: can the catalog route this skill, can the model act on
the body, can the harness trace its source, and are non-negotiable controls
implemented elsewhere?

Next, we will wire that contract into the loop.

## Demonstration cue

Open `examples/skill_template.md`, then compare its routing description with
the body. Show `demo/catalog.py` only after the authoring contract is clear.

## Transition line

> A skill file becomes useful only when the harness can discover, validate,
> load, and trace it safely.
