# Chart and Evidence Panel Specifications

Module 6 is primarily architectural, so charts should support operational
evidence rather than invent aggregate performance claims from three scenarios.

## 1. Scenario outcome matrix

**Purpose:** Show execute, deny, and block as three required outcomes.  
**Form:** Three-row table, not a bar chart.

| Scenario | Permission | Safety | Handler | Final deployment | Completion |
| --- | --- | --- | --- | --- | --- |
| Safe | Allow | Allow | Executed | v41 | Pass |
| Unauthorized | Deny | Not reached | Not executed | v42 | Pass |
| Unsafe | Allow | Block | Not executed | v42 | Pass |

**Required footnote:** Expected results; replace with observed results during a
live recording. “Not reached” must not be rendered as allow.

## 2. Artifact evidence panel

**Purpose:** Reconcile one run without showing sensitive prompt content.  
**Form:** Four cards.

| Card | Fields |
| --- | --- |
| State | scenario, current deployment, rollback performed, recovery confirmed |
| Trace | permission rule, hook code, executed flag, completion status |
| Usage | model, provider, API calls, input/output tokens, estimated cost |
| Summary | return code, completed, final deployment, denial/block counts |

**Rules:**

- show the scenario name and timestamp;
- redact credentials and unnecessary model inputs;
- label the summary “derived”;
- mark absent fields as unavailable, never zero; and
- highlight disagreements across cards.

## 3. Lifecycle event strip

**Purpose:** Show order for one mutation proposal.  
**Form:** Horizontal event strip with timestamps or sequence numbers.

For safe rollback:

```text
permission allow | repeat allow | safety allow | tool executed | completion pass
```

For unauthorized rollback:

```text
permission deny | downstream not reached | completion pass
```

For unsafe rollback:

```text
permission allow | repeat allow | safety block | tool not executed | completion pass
```

Do not draw an event that is absent merely to make rows symmetrical.

## 4. Verification coverage board

**Purpose:** Show which claim each test layer covers.  
**Form:** Matrix with claim columns and test-layer rows.

Claims:

- package matches declarations;
- permission branches work;
- safety branches work;
- handler mutation works;
- completion oracle works;
- CLI integration reaches boundary;
- state and trace reconcile.

Use full circles for direct proof, half circles for supporting evidence, and
empty cells for no coverage. Include a legend that says supporting evidence is
not a substitute for direct proof.

## 5. Operational trend charts for a real deployment

These charts are extensions, not populated by the three-case local demo:

- completion rate by plugin version and scenario class;
- permission denials by rule, subject role, and tool;
- safety blocks by deterministic code;
- incomplete runs by last reached boundary;
- verification nudges per run;
- repeated-call blocks per run;
- model calls, tokens, latency, and estimated cost distributions; and
- state/trace reconciliation failures.

**Required production dimensions:** timestamp, environment, plugin version,
runtime version, model route, toolset, scenario/task class, and correlation ID.

**Privacy rule:** Do not use raw prompts, tool arguments, identities, or tool
results as chart labels. Aggregate or pseudonymize them according to the
organization's data policy.

## 6. Exercise comparison panel

**Purpose:** Compare integration ownership after parity.  
**Form:** Responsibility matrix, followed by observed test status.

Do not graph the captured 0.085 versus 0.090 second behavioral-test times. The
difference is too small and the harness runs used different model routes. Do
not treat saved model cycle counts as stable performance estimates.

Approved quantitative statements are limited to exact current test output and
must identify whether the evidence is deterministic or a saved live capture.
