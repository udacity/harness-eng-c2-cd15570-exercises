# Video 1 — Skills as Task-Specific Context

**Target duration:** 6 minutes  
**Learning objective:** Decide when reusable guidance belongs in a skill and
explain progressive disclosure without claiming guaranteed improvement.

## Instructor narration

### [Slide 1] One request, four manuals — 0:00–0:50

Return to incident `INC-2048`. Production `checkout-api` is degraded, and the
team can ask for a diagnosis, a remediation plan, or a stakeholder update.

Our harness has four detailed guidance files: incident triage, the checkout
runbook, safe remediation, and incident communications. The simplest design
places all four files in every prompt. That works, but a stakeholder update now
receives diagnostic and remediation procedures it may not need.

This is the context problem Module 2 addresses: how do we keep reusable
expertise available without making every task carry the entire library?

### [Slide 2] What a skill is — 0:50–1:45

In this course, a skill is a named package of model-facing instructions. It
captures a repeatable way of working: what evidence to gather, which steps to
follow, what mistakes to avoid, and what output to produce.

A skill is not the model itself. It is not a business tool, and loading it does
not restart a service or send a message. It is context the model can use while
producing a response.

The `incident_communications` skill, for example, teaches the model to lead
with confirmed impact, separate facts from hypotheses, distinguish planned
actions from completed actions, and end with a useful next step. Those are
stable communication procedures. The current incident status and error rate
remain authoritative runtime data, not facts to bake into the skill.

### [Slide 3] When guidance should become a skill — 1:45–2:40

Use a skill when guidance is reusable across tasks, specialized enough that not
every request needs it, and detailed enough that repeating it in the base
prompt would make that prompt harder to maintain.

Good skill candidates include a diagnostic workflow, a brand voice, a document
format, or a domain-specific review checklist.

Keep a rule in the base instructions when it is short and universal. Retrieve
fresh data through a tool. Put actual side effects behind business tools. Put
authorization in a permission boundary. Put exact execution invariants in
hooks. Put final acceptance in checks and evaluators.

This classification matters because a long instruction file cannot substitute
for current evidence or executable enforcement.

### [Slide 4] Progressive disclosure — 2:40–3:45

Progressive disclosure separates the small routing layer from the detailed
instruction layer.

At discovery time, the harness reads each skill's name and description. Those
compact records form a catalog. For the current task, the model sees that
catalog and can request the relevant exact names. Only then does the harness
load complete instructions.

The broader Agent Skills format can add a third layer: supporting references,
scripts, and assets loaded only when needed. This repository intentionally
implements the first two layers only. Each skill is one `SKILL.md`; loading it
returns text. No script executes automatically.

The important engineering property is staged context: enough information to
choose first, then enough information to perform the task.

### [Slide 5] Three events, three meanings — 3:45–4:35

Do not collapse discovery, activation, and use.

Discovery means the harness found and validated a skill package. Activation or
selection means the router or model chose that skill for this task. Loading
means the full instructions entered the model interaction. Following means the
final behavior actually reflected those instructions.

A log that says `incident_communications` was loaded proves only the loading
event. It does not prove the update is accurate. The model can ignore, combine,
or misapply instructions. The final output still needs evaluation.

This vocabulary prevents a common measurement error: counting a selected
component as a successful task.

### [Slide 6] Eager versus on-demand — 4:35–5:30

The Module 2 demo compares two serving paths.

The basic path reads all four complete skills and makes one writing call. It is
simple and has no routing miss, but it always pays for all skill text and may
place competing instructions in context.

The skills path makes a selection call over short descriptions, validates and
loads the requested files, and makes a second writing call. It may supply less
detailed context, but it adds latency, tokens for routing, and a new failure
mode: selection can be wrong.

Neither path is automatically better. The experiment must inspect final
quality as well as context size, tokens, and time.

### [Slide 7] The first design rule — 5:30–6:00

The first design rule is therefore simple: make a skill a focused unit of
reusable know-how, not a storage place for every instruction associated with a
domain.

In the next lesson, we will draw the most important boundary in this module.
A skill may tell the model how to behave. A hook can control what the harness
allows to happen.

## Demonstration cue

Open `demo/skills/incident_communications/SKILL.md`, then show the four-line
catalog produced by `catalog_prompt()`. Do not run the model yet.

## Transition line

> Skills make expertise available at the right time. They do not turn advice
> into enforcement.
