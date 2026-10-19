# Storyboard — Video 3: Authorize Every Proposed Invocation

**Target runtime:** 7 minutes  
**Visual motif:** A four-input decision diamond: subject, action, resource,
context.

## Slide 1 — One exact question

**Time:** 0:00–0:35  
**On-screen text:** May this subject perform this action on this resource now?  
**Visual:** Four labeled inputs converge on `ALLOW / DENY`.

## Slide 2 — Trusted subject

**Time:** 0:35–1:20  
**Visual:** Verified application identity enters policy. Prompt and arguments
hit a red trust-boundary wall.  
**Labels:** user ID, role, tenant, session/elevation status.

## Slide 3 — Exact action mapping

**Time:** 1:20–2:00  
**Visual:**

```text
rollback_deployment -> deployment.rollback
update_incident_status -> incident.status.update
unknown_tool -> DENY
```

**Callout:** No permissive default handler.

## Slide 4 — Trusted resource resolution

**Time:** 2:00–2:55  
**Visual:** Model supplies only `P-1042`; server lookup supplies owner
`USR-101`. A forged `owner_user_id` argument is discarded.  
**On-screen text:** Identify from input; authorize from trusted state.

## Slide 5 — Ownership is one predicate

**Time:** 2:55–3:45  
**Visual:** Two checks in series for contractor edit.

```text
owns P-1042? yes
has permit.edit_own? yes
=> ALLOW
```

Then approval:

```text
owns P-1042? yes
has permit.approve? no
=> DENY
```

## Slide 6 — Fresh context

**Time:** 3:45–4:25  
**Visual:** Policy clock and changing resource version. Cached `ALLOW` expires
before a revocation marker.  
**Labels:** policy version, tenant, environment, elevation expiry, resource
version.

## Slide 7 — Fail closed

**Time:** 4:25–5:10  
**Visual:** Decision result switch with only `ALLOW` connected forward.

```text
DENY / ERROR / UNKNOWN / EXPIRED -> STOP
ALLOW -> next gate
```

**Callout:** Availability fallback is policy, not an accident.

## Slide 8 — Enforcement branch

**Time:** 5:10–6:10  
**Visual:** Highlight `handle_tool_call()` path: parse, permission check,
immediate return on denial, shared dispatch on allow.  
**On-screen result:** `permission_denied`, `executed: false`, matching call ID.

## Slide 9 — Independent actions

**Time:** 6:10–6:40  
**Visual:** Supervisor plan splits:

- approve `P-1042` → `ALLOW` → executed;
- issue `P-1042` → `DENY` → not executed.

Final state badge: `APPROVED`.

## Slide 10 — Takeaway

**Time:** 6:40–7:00  
**On-screen text:** Authority belongs to the exact call, not the conversation.  
**Transition:** Next: compose authorization with the rest of the loop.

## Production notes

- Use actual fictional IDs from the exercise.
- Do not call authorization deterministic without listing its fixed trusted
  inputs and policy version.
- Repository capture: `demo/permissions.py`, `demo/agent.py`, and
  `solution/permissions.py`.
