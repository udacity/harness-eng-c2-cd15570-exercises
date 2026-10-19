# Sources and Research Notes

Accessed October 18, 2026. Recheck changing guidance and repository behavior
before final recording.

## R1 — Module 4 incident authorization

Primary local sources:

- `module-4-permissions/demo/README.md`
- `module-4-permissions/demo/data.py`
- `module-4-permissions/demo/permissions.py`
- `module-4-permissions/demo/agent.py`
- `module-4-permissions/demo/tools.py`
- `module-4-permissions/demo/hooks.py`
- `module-4-permissions/demo/test_demo.py`

**Relevant use:** Defines the trusted incident identities, exact role and tool
mappings, assigned-resource exception, authorization-before-hook order,
structured denials, and controlled basic/permissions comparison.

**Guardrail:** The demo is an in-memory teaching system. Authentication,
production policy distribution, real credentials, and durable state are out of
scope. Its identical catalogs isolate runtime authorization; they are not a
recommendation to expose all production tools.

## R2 — Permit exercise and solution

Primary local sources:

- `module-4-permissions/exercise-permisions-starter/INSTRUCTIONS.md`
- `module-4-permissions/exercise-permisions-starter/test_permissions.py`
- `module-4-permissions/solution/permissions.py`
- `module-4-permissions/solution/agent.py`
- `module-4-permissions/solution/tools.py`
- `module-4-permissions/solution/test_permissions.py`

**Relevant use:** Defines the role matrix, tool mapping, contractor ownership
rules, fail-closed behavior, pre-dispatch enforcement, and independent
multi-action decisions.

**Guardrail:** The exercise tools simplify workflow rules to focus on
authorization. An authorization allow is not proof that a real permit
transition is legally or operationally valid.

## R3 — OWASP authorization guidance

**OWASP Foundation.** “Authorization Cheat Sheet.”  
[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

**Relevant use:** Supports least privilege, deny by default, permission checks
on every request, resource-specific access checks, safe authorization-failure
handling, logging, and unit/integration testing.

**Guardrail:** The course applies general application-security guidance to a
model/tool harness. OWASP does not prescribe this repository's Python API or
its role names.

## R4 — Authorization decision and enforcement patterns

**OWASP Foundation.** “Authorization Patterns Cheat Sheet.”  
[OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Patterns_Cheat_Sheet.html)

**Relevant use:** Supports separating a policy decision point from a policy
enforcement point, keeping enforcement close to the resource, using trusted
subject and resource attributes, denying when no valid decision is available,
covering alternate paths, and logging policy/version context.

**Guardrail:** A separate policy service is optional. Small systems can keep
centralized decision and enforcement logic in application code while retaining
the same security properties.

## R5 — NIST least privilege and access enforcement

**National Institute of Standards and Technology.** “Security and Privacy
Controls for Information Systems and Organizations,” SP 800-53 Rev. 5,
Update 1.  
[NIST CSRC publication](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)

**Relevant use:** AC-3 supports enforcing approved authorizations for logical
access. AC-6 supports limiting users and processes acting for users to the
access necessary for assigned tasks.

**Guardrail:** This course does not claim compliance with NIST SP 800-53.
Control selection, implementation, assessment, and organizational policy are
larger activities than the module exercise.

## R6 — NIST zero trust architecture

**National Institute of Standards and Technology.** “Zero Trust Architecture,”
SP 800-207.  
[NIST CSRC publication](https://csrc.nist.gov/pubs/sp/800/207/final)

**Relevant use:** Supports avoiding implicit trust and treating authentication
and authorization as distinct functions focused on access to protected
resources.

**Guardrail:** A permission-aware agent loop is not, by itself, a zero trust
architecture. The course uses only the relevant resource- and identity-focused
principles.

## Claim-to-source map

| Course claim | Source | Approved phrasing |
| --- | --- | --- |
| Capability does not establish user authority | R1, R2 | “Tool exposure permits proposal; policy governs execution.” |
| Trusted identity does not come from request text | R1, R2 | “The harness receives identity from application state.” |
| Deny by default and check every call | R3, R4 | “Only a current explicit allow may proceed.” |
| Resource ownership changes an authorization result | R2, R3 | “Resolve the requested object and compare trusted attributes.” |
| Decision and enforcement are separate responsibilities | R1, R4 | “The boundary must enforce the policy result before dispatch.” |
| Minimize tool capability by production entitlement | R3, R5 | “Offer only tools plausibly needed, then authorize every call.” |
| Authentication is distinct from authorization | R1, R3, R6 | “Verified identity is an input to, not a substitute for, authorization.” |
| Permission and safety decisions are different | R1 | “Authorized can still be unsafe; safe can still be unauthorized.” |

## Citation and recording policy

1. Identify repository-specific behavior as repository-specific.
2. Describe catalog filtering as defense in depth, not sufficient enforcement.
3. Do not claim NIST compliance or zero trust adoption from this module alone.
4. Do not describe a role name as a wildcard beyond its explicit grants.
5. Do not imply a policy allow guarantees successful or safe execution.
6. Mark synthetic traces, diagrams, and metrics as illustrative.
7. Recheck external links and any changing guidance before recording.
8. Keep quotations short; prefer paraphrase and local code evidence.
