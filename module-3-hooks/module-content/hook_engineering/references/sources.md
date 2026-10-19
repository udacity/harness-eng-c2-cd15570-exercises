# Sources and Research Notes

Accessed October 18, 2026. Recheck changing API documentation before final
recording.

## R1 — Repository definition of hooks and antidotes

Primary local sources:

- `module-3-hooks/solution/README.md`
- `module-3-hooks/solution/hooks.py`
- `module-3-hooks/exercise-hooks-starter/test_hooks.py`

**Relevant use:** Defines the course's “antidote” terminology, expense-policy
checks, exact threshold behavior, `HookResult`, fail-closed malformed input,
and no-network deterministic tests.

**Guardrail:** “Antidote” is a course design term, not a universal framework or
provider primitive.

## R2 — Incident before-tool implementation

Primary local sources:

- `module-3-hooks/demo/hooks.py`
- `module-3-hooks/demo/agent.py`
- `module-3-hooks/demo/tools.py`
- `module-3-hooks/demo/scenarios/*.json`

**Relevant use:** Authoritative source for the five incident invariants, exact
hook placement, controlled block outputs, mutation signatures, freshness
invalidation, serialized tool calls, and execution summaries.

**Guardrail:** The demo is an in-memory teaching system. It does not by itself
solve distributed concurrency, durable idempotency, or authorization.

## R3 — OpenAI function calling

**OpenAI.** “Function calling.”  
[Official OpenAI documentation](https://developers.openai.com/api/docs/guides/function-calling)

**Relevant use:** Supports the application-owned tool-calling sequence: receive
zero or more model function calls, execute application code, correlate outputs
using `call_id`, and continue the conversation. It also supports application
argument validation and explicit tool-choice controls.

**Guardrail:** Function calling does not automatically run the course hook or
enforce business policy. The application inserts the hook before its own tool
dispatcher.

## R4 — Exact decimal arithmetic

**Python Software Foundation.** “`decimal` — Decimal fixed-point and
floating-point arithmetic.”  
[Python documentation](https://docs.python.org/3/library/decimal.html)

**Relevant use:** Supports using decimal representation and arithmetic for
cent-precise expense rules instead of relying on binary floating-point
approximations.

**Guardrail:** `Decimal` accepts special values such as NaN and infinity. The
course parser explicitly rejects non-finite values and fractions of a cent;
using `Decimal` alone is not sufficient validation.

## R5 — Time-of-check/time-of-use risk

**MITRE.** “CWE-367: Time-of-check Time-of-use Race Condition.”  
[CWE-367](https://cwe.mitre.org/data/definitions/367.html)

**Relevant use:** Supports the warning that shared resource state may change
between validation and use, invalidating a prior decision.

**Guardrail:** The course applies the general check/use concept to production
state mutations. It does not claim that every separate hook-and-tool operation
is exploitable; architecture and concurrency determine the risk.

## R6 — Risk management and repeatable evaluation

**NIST.** “AI Risk Management Framework Core.”  
[NIST AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) ·
[AI RMF resources](https://www.nist.gov/itl/ai-risk-management-framework)

**Relevant use:** Supports documenting limitations and using repeatable test,
evaluation, verification, and validation processes alongside monitoring and
safe-failure behavior.

**Guardrail:** NIST does not prescribe this repository's specific hook API or
antidote structure. The course maps general lifecycle practices to its local
implementation.

## Claim-to-source map

| Course claim | Source | Approved phrasing |
| --- | --- | --- |
| An antidote is one exact Python defense against a known failure | R1 | “This course calls the check an antidote.” |
| The incident hook blocks before permissive mutation tools | R2 | “The Module 3 demo follows this order.” |
| Function calls are application-handled and outputs are call-correlated | R3 | “The harness executes or blocks and returns a matching result.” |
| Decimal supports exact decimal representations | R4 | “Use validated `Decimal` values for cent policy.” |
| State can change between check and use | R5 | “Shared-state systems may require atomic conditional execution.” |
| Controls need repeatable testing and monitored limitations | R6 | “Document, evaluate, monitor, and fail safely.” |

## Citation and recording policy

1. Identify repository-specific behavior as repository-specific.
2. Cite official OpenAI documentation only for API mechanics, not hook policy.
3. Present determinism as fixed-input reproducibility, not correctness or total
   agent predictability.
4. Mark every synthetic metric as illustrative.
5. Recheck external links and API behavior before recording.
6. Keep source quotations short; prefer paraphrase and local code evidence.
