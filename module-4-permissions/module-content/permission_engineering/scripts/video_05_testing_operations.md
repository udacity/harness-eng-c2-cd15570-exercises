# Video 5 — Test and Operate Least-Privilege Tool Access

**Target runtime:** 6 minutes  
**Teaching purpose:** Turn permission-aware tool access into a continuously
verified production control.

## Opening

An authorization function can look correct and still leave a production loop
open. The policy may omit a new tool. A denial branch may fall through to
dispatch. A cached grant may outlive revocation. One alternate endpoint may
bypass the check.

Testing must prove both the decision and its enforcement.

## Test the permission matrix exhaustively

Start with deterministic unit tests. The permit solution tests every role
against its allowed and denied tools. Contractors receive an extra resource
dimension: the same edit is allowed for owned `P-1042` and denied for unowned
`P-2095`.

Test both positive and negative cases. A suite containing only authorized
examples proves almost nothing about least privilege.

Add a coverage invariant: the exposed business-tool names, handler registry,
and permission mapping must match. When a developer adds a tool but forgets
policy, the build should fail. Deny-by-default runtime behavior is necessary,
but an alerting build failure finds the governance gap earlier.

## Test trusted identity and resources

Run the impersonation case. The request claims administrator status, but the
decision still uses the trusted contractor or support-engineer identity.

Try forged ownership fields, wrong tenants, unknown resource IDs, empty IDs,
objects in place of strings, and resources the user cannot see. Resolve
security attributes from server-side state.

Be careful when asserting denial messages. The security property is denial and
no execution. Exact user-facing detail may vary to avoid information leakage.

## Test the enforcement integration

A policy unit test can return `DENY` while a broken caller ignores it. Patch or
spy on the dispatcher and assert it was not invoked. Compare protected state
before and after. Verify the safety hook also did not run when authorization
failed first.

Then inspect the returned tool result. It must use the same call ID, say
`permission_denied`, and set `executed` to false. The next model cycle must see
that result rather than fabricated success.

Test multi-action requests. The solution approves `P-1042` for a supervisor,
then independently denies issuance. Final state must be `APPROVED`, not
`PERMIT_ISSUED`. This catches accidental session-level or plan-level grants.

## Test catalog minimization without trusting it

Assert each role receives the intended smallest catalog. An unknown role should
receive none. A new unmapped tool should fail catalog construction or startup.

Then bypass the catalog in the test and call the enforcement boundary directly.
The hidden operation must still be denied. Repeat after revoking a grant while
holding a previously built catalog. Runtime policy must win.

This pair of tests demonstrates the architecture:

```text
catalog filter = reduced opportunity
runtime check  = enforced authority
```

## Test failure and revocation

Production policy dependencies fail. Simulate timeouts, malformed results,
unknown outcomes, expired policies, missing relationship data, and stale
elevation. Confirm none becomes `ALLOW`.

Measure revocation. When a role, scope, or temporary approval is removed, how
long can an existing session, catalog, decision cache, credential, or queued
operation continue? Define freshness budgets and test the worst case.

If an architecture deliberately permits some low-risk read during a policy
outage, document that exact exception and test its limits. Do not use a broad
fail-open switch.

## Operate with evidence

Monitor proposal, decision, and execution counts separately. Useful signals
include:

- denials by subject, action, resource class, and reason code;
- calls to tools absent from the current catalog;
- policy errors and latency;
- tool-to-policy coverage failures;
- repeated cross-resource access attempts;
- use of temporary elevation;
- differences between authorization and downstream service decisions; and
- any event where execution occurred without a recorded explicit `ALLOW`.

Alerting requires context. A spike in denials may be an attack, a broken UI, a
stale role assignment, a newly tightened policy, or a model repeatedly choosing
the wrong tool. The trace should let operators distinguish them.

Version the policy and include that version in decision evidence. Review role
grants, ownership rules, tool mappings, catalog logic, and downstream
credentials as one change set. A permission name in code without the matching
production grant—or the reverse—creates drift.

## Human elevation and approvals

Some actions require more than a static role. Represent approval as trusted,
bounded state: who approved, for which subject, action, resource, environment,
reason, and time window. Re-authorize the final call against that record.

A chat message saying “approved” is not an approval record. The model should
not turn conversational language into elevated authority.

## Closing

A permission-aware loop is production-ready only when the organization can
answer three questions with evidence:

1. Why was this tool available to this principal?
2. Why was this exact invocation allowed or denied?
3. Did the protected operation actually execute?

Least privilege is not a prompt. It is a maintained relationship between
identity, policy, catalog, enforcement, credentials, tests, and audit evidence.

## On-screen repository anchors

- `demo/test_demo.py`: cumulative incident authorization tests
- `solution/test_permissions.py`: role, ownership, denial, and loop tests
- `examples/permission_test_matrix.md`: production extension
- `examples/sample_permission_results.md`: evidence interpretation
