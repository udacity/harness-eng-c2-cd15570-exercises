# Storyboard — Video 5: Test and Operate Least-Privilege Tool Access

**Target runtime:** 6 minutes  
**Visual motif:** A verification dashboard built from policy, integration,
failure, and production evidence.

## Slide 1 — Decision correct, boundary broken

**Time:** 0:00–0:35  
**Visual:** Policy returns `DENY`, but a broken arrow bypasses it and reaches the
tool.  
**On-screen text:** Test enforcement, not only policy output.

## Slide 2 — Matrix coverage

**Time:** 0:35–1:15  
**Visual:** Role-by-action heatmap with both green allow and red deny cells.  
**Callout:** Positive-only tests do not prove least privilege.

## Slide 3 — Resource and impersonation tests

**Time:** 1:15–2:00  
**Visual:** Alex versus two applications, plus an “I am administrator” speech
bubble that cannot alter the trusted identity badge.  
**Labels:** own `ALLOW`, other `DENY`, forged role ignored.

## Slide 4 — No-execution proof

**Time:** 2:00–2:45  
**Visual:** Denial assertion checklist:

- dispatcher calls: 0;
- hook calls: 0;
- state diff: empty;
- output: `executed=false`;
- call ID: matches.

## Slide 5 — Catalog bypass test

**Time:** 2:45–3:25  
**Visual:** Hidden issue tool is injected directly; runtime gate denies it. A
second frame revokes a grant after catalog creation and produces the same deny.  
**Callout:** Visibility is defense in depth.

## Slide 6 — Failure and revocation

**Time:** 3:25–4:10  
**Visual:** Timeout, malformed decision, expired elevation, and stale cache all
flow to `NO EXECUTION`.  
**On-screen question:** How long can old authority survive?  
**Answer label:** Define and test the freshness budget.

## Slide 7 — Production signals

**Time:** 4:10–5:00  
**Visual:** Illustrative dashboard with no numeric benchmark claims:

- proposal/allow/deny/execute counts;
- policy errors and latency;
- cross-resource denials;
- catalog-bypass proposals;
- execution without allow: zero target.

## Slide 8 — Govern change together

**Time:** 5:00–5:30  
**Visual:** One review bundle: tool schema + handler + permission mapping +
role grants + tests + credential scope + audit fields.  
**Callout:** Version the effective policy.

## Slide 9 — Final questions

**Time:** 5:30–6:00  
**On-screen text:**

1. Why was the tool available?
2. Why was this call allowed or denied?
3. Did it execute?

**End card:** Least privilege is an enforced system property, not a prompt.

## Production notes

- Label all dashboard values “illustrative.”
- Code capture: `solution/test_permissions.py` denial and multi-action tests.
- End on the three evidence questions for continuity into Module 5 evaluation.
