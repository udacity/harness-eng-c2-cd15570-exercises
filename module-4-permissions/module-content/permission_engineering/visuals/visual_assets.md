# Visual Asset Plan

## Required reusable assets

- Neutral model node labeled “proposal generator.”
- Tool cards for read, write, rollback, status update, approve, and issue.
- Trusted identity badge with subject ID, role, and tenant slots.
- Permission token displaying an exact grant such as `permit.approve`.
- Resource cards with owner, assignment, tenant, state, and version fields.
- Authorization shield with `ALLOW`, `DENY`, and `ERROR` states.
- Safety-hook gate distinct from the authorization shield.
- Allowlisted dispatcher and downstream service nodes.
- Structured tool-result envelope with call-ID tab.
- Evidence ledger and state-diff panel.

## Color and shape system

| Meaning | Color | Shape/label |
| --- | --- | --- |
| Proposal/untrusted | Amber | Dashed outline, `PROPOSED` |
| Trusted application data | Blue | Solid rectangle, `TRUSTED` |
| Explicit authorization allow | Green | Shield/check, `ALLOW` |
| Authorization denial/error | Red | Shield/stop, `DENY` or `ERROR` |
| Safety block | Purple | Octagon, `BLOCKED` |
| Not performed | Gray | Muted stage, `NOT RUN` |
| Confirmed execution | Dark green | Filled event, `EXECUTED` |

Color must never carry meaning alone.

## Code-capture plan

Capture short excerpts rather than entire files:

1. `demo/data.py`: one trusted user entry.
2. `demo/permissions.py`: role grants and one tool mapping.
3. `demo/permissions.py`: assignment check.
4. `demo/agent.py`: immediate return after denial.
5. `demo/agent.py`: authorization before hook and dispatch.
6. `solution/permissions.py`: contractor `_own` mapping.
7. `solution/test_permissions.py`: no-mutation denial assertion.
8. `solution/test_permissions.py`: approve-then-issue independent decisions.
9. `examples/permission_aware_catalog.py`: catalog filter and coverage check.

Use line highlighting and a monospace size readable at 1080p. Redact `.env`,
tokens, local usernames, and absolute home paths.

## Demo capture plan

Record these sequences from clean state:

- `unauthorized_rollback`: basic versus permissions;
- `commander_rollback`: authorization and safety both allow;
- `commander_premature_resolution`: authorization allows, safety blocks;
- `unassigned_read`: resource assignment denies;
- `impersonation_attempt`: trusted identity defeats request-text claim;
- permit supervisor approval followed by denied issuance.

Do not pre-label a model-dependent action. Reveal the actual proposal and
result from the run log.

## Accessibility and editorial checks

- Minimum contrast ratio follows course accessibility requirements.
- Every icon has an adjacent text label.
- Diagrams remain legible in grayscale.
- Reading order follows narration direction.
- Avoid flashing authorization states.
- Define RBAC, ABAC, PEP, and PDP before using acronyms, or omit the acronyms.
- Use “principal” only after defining it as an authenticated user or workload.
- Never show real credentials, organization data, or production resource IDs.

## Third-party assets

No third-party image is required. Prefer original vector shapes, repository
code captures, and fictional data already supplied by the course. Record any
later external icon or illustration in the course's third-party asset ledger
before publication.
