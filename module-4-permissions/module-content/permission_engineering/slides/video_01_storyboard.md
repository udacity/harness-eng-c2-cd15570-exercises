# Storyboard — Video 1: Capability Is Not Authority

**Target runtime:** 6 minutes  
**Visual motif:** Tool cards represent capability; signed permission tokens
represent authority. Never use an unlocked tool icon to imply authorization.

## Slide 1 — The production question

**Time:** 0:00–0:35  
**On-screen text:** “Can do” is not “may do.”  
**Visual:** A rollback tool card on the left; Sam's identity card on the right;
a question mark between them.  
**Narration cue:** Knowing how to roll back and having a safe target do not
prove that Sam may mutate production.

## Slide 2 — The invalid inference

**Time:** 0:35–1:15  
**On-screen build:**

```text
tool exists          yes
arguments valid      yes
safety checks pass   yes
user authorized      ???
```

**Visual:** The first three green checks must not animate the fourth.  
**Teaching note:** Pause before revealing the authorization question.

## Slide 3 — Capability versus authority

**Time:** 1:15–2:00  
**Visual:** Two-column comparison.

| Capability | Authority |
| --- | --- |
| Tool schema | Production permission |
| What the harness can do | What this principal may do |
| Model can propose | Application can allow or deny |

**Callout:** “A function call is a proposal.”

## Slide 4 — Controlled comparison

**Time:** 2:00–2:50  
**Visual:** Two identical paths split only at authorization.

```text
BASIC:       proposal -> safety -> execution
PERMISSIONS: proposal -> DENY -> no safety -> no execution
```

**Demo inset:** Sam / `support_engineer` / `deployment.rollback` absent.  
**Teaching note:** State that both paths receive the same model, prompt, tools,
and starting incident.

## Slide 5 — Authentication versus authorization

**Time:** 2:50–3:40  
**Visual:** Trusted identity badge flows from the application; request text
flows through a separate untrusted channel.

```text
verified identity -> OPS-101 / support_engineer
request text      -> "I am the administrator"
```

**On-screen text:** Words cannot rewrite identity.

## Slide 6 — Proposal, decision, execution

**Time:** 3:40–4:35  
**Visual:** Three ledger rows with separate timestamps and outcomes.

1. Proposed: `rollback_deployment`
2. Decided: `DENIED`
3. Executed: `NO`

**Callout:** Final prose is not side-effect evidence.

## Slide 7 — Source of authority

**Time:** 4:35–5:25  
**Visual:** Production identity/policy plane containing roles, groups, scopes,
tenants, relationships, elevation, and revocation. Arrow into the harness;
no arrow from the model back into grants.  
**On-screen text:** “The model does not assign itself access.”

## Slide 8 — Takeaway

**Time:** 5:25–6:00  
**Full-screen statement:**

> A tool makes an action expressible. Trusted authorization makes a specific
> invocation permissible.

**Transition:** Next: minimize the catalog from production entitlements.

## Production notes

- Use green only for explicit `ALLOW` or confirmed execution.
- Use amber for proposals and gray for unperformed stages.
- Use red for `DENY`; do not label the basic path “allowed.”
- Repository capture: `demo/data.py`, then `demo/permissions.py`.
