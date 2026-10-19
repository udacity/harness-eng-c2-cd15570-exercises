# Skill Harness Test and Evaluation Matrix

## Deterministic integration tests

| Boundary | Test | Expected evidence |
| --- | --- | --- |
| Discovery | Valid directories are found in stable order | Exact catalog names |
| Metadata | Missing delimiter, name, or description | Startup/configuration failure |
| Identity | Name differs from parent directory | Rejected skill |
| Uniqueness | Duplicate name appears | Catalog build fails |
| Filesystem | Skill or parent is a symlink | Rejected or excluded per policy |
| Catalog isolation | Build routing prompt | Names/descriptions present; bodies absent |
| Schema | Inspect `load_skill` definition | One required string; no extra properties |
| Allowlist | Request known exact name | Full text plus provenance returned |
| Traversal | Request `../secret` | Controlled error; no filesystem access |
| Malformed arguments | Invalid JSON or wrong shape | Controlled correlated error |
| Multiple selection | Request two valid skills | Both results returned with correct call IDs |
| Duplicate selection | Request the same skill twice | Deduplicated or controlled error per policy |
| Zero selection | Model makes no call | Final cycle still runs under fallback policy |
| Boundary closure | Inspect final writing request | Loader is absent |
| Limits | Oversized body or too many selections | Fail-closed limit result |
| Logging | Complete one run | Names, sources/versions, sizes, errors, cycles recorded |

## Behavioral evaluation set

Create task labels independently of model selection:

| Task | Relevant skills |
| --- | --- |
| Diagnose checkout failures | `incident_triage`, `checkout_service_runbook` |
| Write stakeholder update | `incident_communications` |
| Plan cautious rollback | `incident_triage`, `checkout_service_runbook`, `safe_remediation` |
| Answer an unrelated greeting | none |

For each repeated run, record selected skills and final-output acceptance.

## Routing metrics

For one task:

```text
true positives  = relevant skills selected
false positives = irrelevant skills selected
false negatives = relevant skills omitted

precision = TP / (TP + FP)
recall    = TP / (TP + FN)
```

Define the zero-selection precision convention before reporting aggregates.
Always show raw counts and task-level results; one average can hide a critical
miss.

## End-task metrics

- final acceptance against the same evaluator or human reference;
- named requirement failures;
- unsupported claims or unsafe recommendations;
- complete skill characters supplied;
- API input, output, and total tokens;
- selection and writing latency separately;
- total serving latency;
- selection errors and fallback frequency; and
- evaluator overhead reported separately from serving work.

## Interpreting results

- High routing recall with low precision may load too much irrelevant context.
- High precision with low recall may omit required guidance.
- Perfect selection does not establish correct final output.
- Fewer loaded characters do not prove fewer total tokens because selection
  adds a model cycle and conversation context.
- Better output in one run does not establish general improvement. Repeat on a
  representative task set and report variability.
- A skill that improves prose but attempts to replace a required enforcement
  boundary is still incorrectly designed.
