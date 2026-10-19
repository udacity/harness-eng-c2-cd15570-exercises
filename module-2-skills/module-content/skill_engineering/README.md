# Skill Engineering in Harness Loops

Instructional collateral for **Module 2: On-Demand Skills and Progressive
Disclosure**.

This package is for instructor review, video recording, slide production, and
exercise alignment. It uses the Module 2 `INC-2048` demo as the running example
and connects it to the InspectAI marketing exercise.

## Teaching thesis

A skill is reusable, model-facing guidance selected for a task. It can improve
reasoning and output by supplying domain procedures at the right time. It is
not an execution guarantee, permission boundary, or deterministic policy gate.

A hook is harness-owned code attached to a lifecycle event. It runs because
the event occurs, not because the model remembers to request it. A hook can
inspect, block, transform, or record an operation. Skills guide model behavior;
hooks enforce application behavior.

Production skill loading therefore requires more than writing a good Markdown
file. The harness must discover trusted skills, expose compact routing
metadata, validate exact selections, load only allowlisted content, preserve
provenance, continue the model loop correctly, handle zero or multiple
selections, and measure whether the added context helps.

## Package map

```text
skill_engineering/
├── README.md
├── module_overview.md
├── learning_objectives.md
├── scripts/       complete narration for five short lessons
├── slides/        slide-by-slide production storyboards
├── visuals/       diagram, chart, and asset specifications
├── examples/      templates, secure loading code, and worked evidence
├── references/    annotated primary and official sources
└── instructor_review.md
```

## Recommended review order

1. Review `module_overview.md` and `learning_objectives.md`.
2. Approve the skills-versus-hooks responsibility table.
3. Review the skill template, loader, and loop pseudocode.
4. Review each narration script beside its storyboard.
5. Resolve `instructor_review.md` before recording.

## Editorial conventions

- **Skill** means a named package of model-facing instructions and optional
  supporting resources.
- **Catalog** means the compact name-and-description routing index.
- **Activation** means choosing a skill for the current task.
- **Loading** means placing the selected skill instructions into model context.
- **Tool** means a callable capability or data interface exposed by the
  harness. In this demo, `load_skill` is a harness tool used to retrieve
  instructions; loading does not perform a business action.
- **Hook** means harness code bound to a lifecycle event such as before a tool
  executes.
- **Progressive disclosure** means exposing routing metadata first, complete
  instructions after activation, and optional resources only when needed.

Observed model behavior must be described as observed. Sample routing results
and metrics in this package are illustrative and are not benchmark claims.

## Repository alignment

The narration references:

- `demo/catalog.py`
- `demo/agent.py`
- `demo/skills/*/SKILL.md`
- `demo/test_demo.py`
- `exercise-skills-starter/catalog.py`
- `exercise-skills-starter/agent.py`
- `exercise-skills-starter/skills/*/SKILL.md`
- `module-3-hooks/demo/hooks.py` for the explicit hook comparison

The demo implements a deliberately small skill profile: one `SKILL.md` per
skill, `name` and `description` frontmatter, and no automatic execution of
bundled scripts or recursive resource loading. Do not imply that it implements
every feature of the broader Agent Skills specification.
