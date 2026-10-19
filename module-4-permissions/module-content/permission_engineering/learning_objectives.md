# Learning Objectives

By the end of Module 4, learners will be able to:

1. **Distinguish capability from authority** by explaining why a tool schema,
   model selection, prompt instruction, or successful argument validation does
   not grant the authenticated principal permission to act.
2. **Separate authentication from authorization** by sourcing identity from
   trusted application state and refusing role or identity claims contained in
   user text or model-generated arguments.
3. **Derive a least-privilege tool catalog** from production roles, scopes, and
   entitlements while explaining why catalog filtering is defense in depth,
   not the final security boundary.
4. **Model authorization as subject, action, resource, and context** using
   explicit role-to-permission, tool-to-permission, and ownership or assignment
   rules.
5. **Enforce every decision before execution** so `DENY`, malformed input,
   unknown policy state, and authorization errors cannot reach a business tool
   or create a side effect.
6. **Authorize multi-step requests independently** without allowing an earlier
   permission grant, tool result, or model claim to confer authority on later
   actions.
7. **Compose permissions with safety hooks** by applying authorization first,
   safety invariants second, and dispatch only after every applicable gate
   returns an affirmative decision.
8. **Return controlled denial evidence** to the model using the matching call
   identifier without leaking unnecessary sensitive policy or resource data.
9. **Design fail-closed tests** that cover every exposed tool, every role,
   allowed and denied resources, impersonation attempts, missing inputs,
   unknown tools, policy errors, and no-mutation guarantees.
10. **Operate the authorization boundary** with versioned policy, revocation,
    decision logging, least-privilege credentials, freshness controls, and
    alerts for repeated or anomalous denials.

## Observable mastery criteria

A learner has met the objectives when they can inspect a proposed tool call and
identify:

- the trusted principal and where it originated;
- the exact action and required production permission;
- the resource and trusted attributes used in the decision;
- whether the tool should have been exposed;
- whether the invocation is allowed now;
- whether a safety hook must run after authorization;
- whether the tool actually executed; and
- which structured evidence proves each answer.

## Misconceptions to correct

- “The model knows the user's role, so it can decide access.”
- “If a tool is visible, the user is allowed to use it.”
- “If a tool is hidden, no other path can invoke it.”
- “Authentication means the user may access every tool.”
- “An administrator automatically has every permission.”
- “A safe operation is necessarily an authorized operation.”
- “A previous `ALLOW` covers the rest of the plan.”
- “Ownership can be trusted from a tool argument.”
- “A policy timeout should fall back to execution for availability.”
- “The final answer proves whether a side effect occurred.”
