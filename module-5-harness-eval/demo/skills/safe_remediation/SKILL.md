---
name: safe_remediation
description: Use for production rollbacks, mutations, and recovery verification.
---

# Safe remediation

Treat every mutation tool call as a proposal to the runtime boundary. Gather
fresh health and relevant deployment evidence, then submit the user's exact
requested mutation once. Do not infer authorization, silently substitute a
safer target, or ask for confirmation; permissions and deterministic hooks make
the authoritative decision. If allowed, verify health afterward. If denied or
blocked, report that no mutation executed and explain the returned reason.
Resolution still requires observed recovery.
