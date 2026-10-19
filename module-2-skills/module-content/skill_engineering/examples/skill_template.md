# Course Skill Template

This template matches the **Module 2 repository implementation**, which uses
underscore names and parses only `name` and `description`. It is not presented
as full conformance with the broader Agent Skills specification.

```markdown
---
name: incident_communications
description: Use when writing an internal or stakeholder incident update, especially when recovery is not yet confirmed.
---

# Incident communications

## Purpose

Create an accurate update for readers who need the current state and next
action without unsupported conclusions.

## Use this skill when

- the user asks for an incident update;
- the audience is internal leadership or external stakeholders; or
- plans, completed actions, and verified outcomes must remain distinct.

## Do not use this skill as

- authorization to change incident state;
- a source of current incident facts;
- a replacement for a communication approval workflow; or
- proof that the finished update is factually correct.

## Required inputs

- authoritative incident identifier and status;
- measured impact and service health;
- confirmed action and recovery state; and
- intended audience.

## Procedure

1. Lead with confirmed state and measured impact.
2. Separate facts, hypotheses, and planned actions.
3. Match detail to the audience without inventing facts.
4. End with one evidence-producing next step.

## Invariants in the response

- Never convert a proposed action into a completed action.
- Never announce recovery unless authoritative state confirms it.
- Preserve uncertainty when root cause is unconfirmed.

## Edge cases

- If no recovery estimate exists, do not invent one.
- If sources conflict, identify the conflict and request authoritative state.
- If the word limit is tight, retain current impact and next step first.

## Output contract

Return only the requested update unless the user asks for analysis.
```

## Authoring checklist

- One responsibility and a recognizable task family.
- A description that says both what it does and when it applies.
- Stable procedure rather than rapidly changing facts.
- Explicit required inputs and evidence boundaries.
- Positive steps plus concrete prohibitions.
- Edge cases that have appeared in evaluations.
- No secrets, credentials, private chain-of-thought, or implicit authority.
- No instruction to bypass base policy, permissions, hooks, or evaluation.
- Examples only when they clarify a decision; examples never become invented
  facts for a new task.
- Owner, version, and change record tracked by the surrounding repository or
  deployment system.

## Description test

Place this description beside every neighboring skill description and ask:

1. Can a reviewer predict when this skill should activate?
2. Are non-triggering tasks distinguishable?
3. Does it overlap another skill so heavily that routing becomes arbitrary?
4. Does it promise an action or enforcement the skill cannot provide?

If the answers are unclear, improve scope before lengthening the body.
