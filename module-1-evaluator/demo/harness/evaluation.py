"""Deterministic checks and strict parsing for model-evaluator output."""

from harness.models import CheckResult, Review, Scenario


SELF_CRITERIA = (
    "INCIDENT_ID",
    "LENGTH",
    "FACTUAL_GROUNDING",
    "USEFUL_NEXT_STEP",
)
EXTERNAL_CRITERIA = ("FACTUAL_GROUNDING", "USEFUL_NEXT_STEP")


def deterministic_checks(candidate: str, scenario: Scenario) -> list[CheckResult]:
    """Evaluate criteria that need no model judgment."""

    requirements = scenario.response_requirements
    expected_id = str(requirements["required_incident_id"])
    minimum = int(requirements["minimum_words"])
    maximum = int(requirements["maximum_words"])
    word_count = len(candidate.split())
    return [
        CheckResult(
            name="INCIDENT_ID",
            passed=expected_id in candidate,
            detail=f"expected exact ID {expected_id}",
        ),
        CheckResult(
            name="LENGTH",
            passed=minimum <= word_count <= maximum,
            detail=f"observed {word_count} words; expected {minimum}-{maximum}",
        ),
    ]


def checks_passed(checks: list[CheckResult]) -> bool:
    return bool(checks) and all(check.passed for check in checks)


def parse_review(text: str, criteria: tuple[str, ...], *, require_verdict: bool) -> Review:
    """Parse exact PASS/FAIL fields and fail closed on missing output."""

    decisions: dict[str, bool] = {}
    feedback = "Evaluator did not provide feedback."
    verdict: bool | None = None
    for line in text.splitlines():
        label, separator, value = line.partition(":")
        if not separator:
            continue
        normalized_label = label.strip().upper()
        normalized_value = value.strip()
        first_word = normalized_value.split(maxsplit=1)[0].upper() if normalized_value else ""
        if normalized_label in criteria and first_word in {"PASS", "FAIL"}:
            decisions[normalized_label] = first_word == "PASS"
        elif normalized_label == "VERDICT" and first_word in {"PASS", "FAIL"}:
            verdict = first_word == "PASS"
        elif normalized_label == "FEEDBACK" and normalized_value:
            feedback = normalized_value

    complete = all(name in decisions for name in criteria)
    parsed_criteria = {name: decisions.get(name, False) for name in criteria}
    if require_verdict:
        final_verdict = complete and all(parsed_criteria.values()) and verdict is True
    else:
        final_verdict = complete and all(parsed_criteria.values())
    if not complete:
        missing = ", ".join(name for name in criteria if name not in decisions)
        feedback = f"Malformed evaluator output; missing: {missing}."
    elif require_verdict and verdict is None:
        feedback = "Malformed evaluator output; missing: VERDICT."

    return Review(
        criteria=parsed_criteria,
        verdict=final_verdict,
        feedback=feedback,
        raw_text=text,
    )
