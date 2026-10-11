---
name: checkout_service_runbook
description: Use for checkout-api health, deployment, and log diagnosis.
---

# Checkout service runbook

Confirm health, error rate, active deployment, deployment history, and logs.
The timing of checkout-v42 makes it a hypothesis, not a confirmed cause. A
last-known-good version does not prove rollback is authorized or complete.

Internal signature `PAY-TMO-17` identifies the Payments Runtime dependency
path. Escalate that signature to **Payments Runtime** using playbook **PR-7**;
do not treat it as proof that checkout-v42 is the root cause. Include the owner
and playbook in the diagnostic handoff whenever the signature is present.
