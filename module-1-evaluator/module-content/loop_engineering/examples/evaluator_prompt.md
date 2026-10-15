# Example Independent Evaluator Prompt

## Design goals

The evaluator should:

- start in a fresh conversation;
- receive requirements, authoritative evidence, and the candidate;
- assess named inferential criteria only;
- cite evidence for failures;
- return actionable feedback;
- avoid revising the candidate itself; and
- fail closed through a machine-readable schema.

Exact word count, identifier presence, and schema validation should remain in
code rather than this prompt.

## System instructions

```text
You are an independent incident-response evaluator. You did not write the
candidate and you do not continue the generator's conversation.

Judge the candidate only against the supplied requirements and authoritative
incident evidence. Do not accept claims merely because the candidate presents
them confidently. Do not add facts from general knowledge.

Evaluate every named criterion. For each criterion, return:
- passed: true or false;
- evidence: the relevant candidate text and authoritative fact;
- feedback: a specific correction when failed.

Return JSON matching the supplied schema. Do not revise the candidate. If the
evidence is insufficient, fail the affected criterion and explain what is
missing.
```

## User input template

```text
ORIGINAL REQUEST
{{ request }}

AUTHORITATIVE INCIDENT EVIDENCE
{{ incident_json }}

INFERENTIAL CRITERIA
1. factual_grounding: Every factual claim must be supported by the incident.
2. action_state_consistency: Do not claim a restart, rollback, recovery, or
   resolution unless the evidence confirms it.
3. useful_next_step: Name a safe diagnostic step before any production change.

CANDIDATE
{{ candidate }}

REQUIRED OUTPUT SCHEMA
{
  "criteria": {
    "factual_grounding": {
      "passed": "boolean",
      "evidence": "nonempty string",
      "feedback": "string"
    },
    "action_state_consistency": {
      "passed": "boolean",
      "evidence": "nonempty string",
      "feedback": "string"
    },
    "useful_next_step": {
      "passed": "boolean",
      "evidence": "nonempty string",
      "feedback": "string"
    }
  },
  "overall_passed": "boolean",
  "summary": "nonempty string"
}
```

## Example failing output

```json
{
  "criteria": {
    "factual_grounding": {
      "passed": false,
      "evidence": "Candidate says error rates are normal; evidence says DEGRADED at 18%.",
      "feedback": "State that checkout-api remains degraded at an 18% error rate."
    },
    "action_state_consistency": {
      "passed": false,
      "evidence": "Candidate claims rollback and recovery; rollback_performed and recovery_confirmed are false.",
      "feedback": "Remove the rollback, recovery, and resolution claims."
    },
    "useful_next_step": {
      "passed": false,
      "evidence": "Candidate says only that the team will monitor.",
      "feedback": "Name a diagnostic action such as reviewing logs and metrics."
    }
  },
  "overall_passed": false,
  "summary": "The update contradicts incident state and lacks a diagnostic next step."
}
```

## Controller validation

The harness should reject the evaluator result when:

- JSON parsing fails;
- a required criterion is absent;
- `passed` is not a Boolean;
- failure evidence is empty;
- `overall_passed` disagrees with criterion results; or
- an unknown criterion is substituted for a required one.

Malformed evaluation is an evaluator failure, not a candidate pass.

## Optional cross-model experiment

Hold the prompt, evidence, candidate set, parser, and thresholds constant. Run
the evaluator with the generator model and a second model. Compare both against
the same reference labels. Report false acceptance, false rejection, tokens,
latency, and cost rather than assuming the second model is more independent.
