# Storyboard — Video 2: Derive Tool Access from Production Permissions

**Target runtime:** 7 minutes  
**Visual motif:** A large catalog narrows through a permission filter, then each
remaining call reaches a separate runtime gate.

## Slide 1 — Least-privilege catalog

**Time:** 0:00–0:40  
**Visual:** Nine permit tool cards narrow to four contractor cards: create,
read, edit, submit.  
**On-screen text:** Offer the smallest useful capability set.

## Slide 2 — Trusted derivation path

**Time:** 0:40–1:30  
**Visual:**

```text
verified identity
    -> roles/scopes/tenant/elevation
    -> production permission mappings
    -> model-visible tools
```

**Annotation:** No prompt-text input enters the permission mapping.

## Slide 3 — Two mappings

**Time:** 1:30–2:20  
**Visual:** Join table animation.

```text
supervisor -> permit.approve
approve_application -> permit.approve
                         |
                      include
```

Then:

```text
supervisor -X-> permit.issue
issue_permit -> permit.issue
                    |
                   omit
```

**Callout:** Role names are not wildcards.

## Slide 4 — Coverage invariant

**Time:** 2:20–2:55  
**Visual:** Three equal sets: schemas, handlers, policy mappings. A new unmapped
tool turns the build red.  
**On-screen text:** New tool + no rule = unavailable, denied, alerted.

## Slide 5 — Resource-scoped ambiguity

**Time:** 2:55–3:55  
**Visual:** Alex can edit `P-1042`; a lock remains on `P-2095`. Both use the
same `edit_application` card.  
**On-screen question:** Should the tool be visible?  
**Reveal:** Yes, potentially; authorize the chosen record at runtime.

## Slide 6 — Filtering is not enforcement

**Time:** 3:55–4:55  
**Visual:** A hidden `issue_permit` card is manually injected past the catalog,
then stopped at the authorization gate.  
**Labels:**

- catalog: reduced opportunity;
- runtime: enforced authority.

## Slide 7 — Demo versus production

**Time:** 4:55–5:40  
**Visual:** Side-by-side.

| Module 4 experiment | Production extension |
| --- | --- |
| Identical tool lists | Permission-derived catalog |
| Isolates authorization | Reduces exposed capability |
| Runtime decision | Runtime decision still mandatory |

## Slide 8 — Bounded credentials

**Time:** 5:40–6:25  
**Visual:** Harness exchanges an allow decision for a narrow, short-lived
credential; a broad admin key is crossed out.  
**On-screen text:** Never retry denial with broader authority.

## Slide 9 — Takeaway

**Time:** 6:25–7:00  
**Full-screen statement:** “Minimize before inference. Authorize again before
execution.”  
**Transition:** Next: evaluate the exact subject, action, and resource.

## Production notes

- Animate cards; do not show real vendor logos.
- Code capture: `examples/permission_aware_catalog.py` lines defining the two
  mappings, filter, and coverage assertion.
- Add a persistent footer after Slide 5: “Visibility ≠ permission.”
