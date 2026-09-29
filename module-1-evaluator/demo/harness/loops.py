"""Basic, self-evaluation, and external-evaluation harness loops."""

from collections.abc import Callable

from harness.evaluation import (
    EXTERNAL_CRITERIA,
    SELF_CRITERIA,
    checks_passed,
    deterministic_checks,
    parse_review,
)
from harness.models import Attempt, ModelReply, RunResult, Scenario
from harness.providers import Provider


Emitter = Callable[[str], None]
Pause = Callable[[], None]


def _no_pause() -> None:
    return None


def _totals(attempts: list[Attempt]) -> tuple[int, int, float]:
    replies: list[ModelReply] = []
    for attempt in attempts:
        replies.append(attempt.candidate)
        if attempt.self_reply is not None:
            replies.append(attempt.self_reply)
        if attempt.external_reply is not None:
            replies.append(attempt.external_reply)
    return (
        sum(reply.input_tokens for reply in replies),
        sum(reply.output_tokens for reply in replies),
        sum(reply.model_seconds for reply in replies),
    )


def _result(
    *,
    mode: str,
    attempts: list[Attempt],
    stop_reason: str,
    accepted: bool | None,
    false_positive_observed: bool = False,
) -> RunResult:
    input_tokens, output_tokens, model_seconds = _totals(attempts)
    return RunResult(
        mode=mode,
        attempts=tuple(attempts),
        final_response=attempts[-1].candidate.text,
        stop_reason=stop_reason,
        accepted=accepted,
        false_positive_observed=false_positive_observed,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model_seconds=model_seconds,
    )


def _show_candidate(attempt: int, maximum: int, candidate: ModelReply, emit: Emitter) -> None:
    emit(f"\n---------------- CYCLE {attempt} OF {maximum} ----------------")
    emit("Generator output:")
    emit(candidate.text)


def run_basic(
    provider: Provider,
    scenario: Scenario,
    *,
    emit: Emitter = print,
    pause: Pause = _no_pause,
) -> RunResult:
    """Run two generation cycles without making a quality judgment."""

    initial = provider.generate_initial(scenario)
    attempts = [Attempt(number=1, candidate=initial)]
    _show_candidate(1, 2, initial, emit)
    emit("Evaluation: NOT PERFORMED")
    pause()

    clarified = provider.clarify(initial, scenario)
    attempts.append(Attempt(number=2, candidate=clarified))
    _show_candidate(2, 2, clarified, emit)
    emit("Evaluation: NOT PERFORMED")
    emit("Stop reason: fixed two-cycle limit; this is not evidence of quality.")
    pause()
    return _result(
        mode="basic",
        attempts=attempts,
        stop_reason="fixed cycle limit reached without evaluation",
        accepted=None,
    )


def run_self(
    provider: Provider,
    scenario: Scenario,
    *,
    max_attempts: int = 2,
    emit: Emitter = print,
    pause: Pause = _no_pause,
) -> RunResult:
    """Let the generator evaluate its own response in the same conversation."""

    candidate = provider.generate_initial(scenario)
    attempts: list[Attempt] = []
    for number in range(1, max_attempts + 1):
        _show_candidate(number, max_attempts, candidate, emit)
        self_reply = provider.self_review(candidate, scenario)
        review = parse_review(self_reply.text, SELF_CRITERIA, require_verdict=True)
        attempt = Attempt(
            number=number,
            candidate=candidate,
            self_reply=self_reply,
            self_review=review,
        )
        attempts.append(attempt)
        emit("\nSelf-evaluator output:")
        emit(self_reply.text)
        emit(f"Self-evaluator verdict: {'PASS' if review.verdict else 'FAIL'}")
        if review.verdict:
            emit("Stop reason: the self-evaluator accepted its own response.")
            pause()
            return _result(
                mode="self",
                attempts=attempts,
                stop_reason="self-evaluator returned PASS",
                accepted=True,
            )
        if number == max_attempts:
            emit("Stop reason: the self-evaluation attempt limit was reached.")
            pause()
            return _result(
                mode="self",
                attempts=attempts,
                stop_reason="self-evaluation attempt limit reached",
                accepted=False,
            )
        pause()
        candidate = provider.revise(candidate, scenario, review.feedback)

    raise AssertionError("self-evaluation loop exited unexpectedly")


def run_external(
    provider: Provider,
    scenario: Scenario,
    *,
    max_attempts: int = 3,
    emit: Emitter = print,
    pause: Pause = _no_pause,
) -> RunResult:
    """Compare self-review with deterministic and independent checks."""

    candidate = provider.generate_initial(scenario)
    attempts: list[Attempt] = []
    false_positive_observed = False

    for number in range(1, max_attempts + 1):
        _show_candidate(number, max_attempts, candidate, emit)

        self_reply = provider.self_review(candidate, scenario)
        self_review = parse_review(
            self_reply.text, SELF_CRITERIA, require_verdict=True
        )
        emit("\nSelf-evaluator output:")
        emit(self_reply.text)

        checks = deterministic_checks(candidate.text, scenario)
        emit("\nDeterministic checks:")
        for check in checks:
            label = "PASS" if check.passed else "FAIL"
            emit(f"{check.name}: {label} ({check.detail})")

        external_reply = provider.external_review(candidate, scenario)
        external_review = parse_review(
            external_reply.text, EXTERNAL_CRITERIA, require_verdict=False
        )
        emit("\nIndependent evaluator output:")
        emit(external_reply.text)

        independent_passed = checks_passed(checks) and external_review.verdict
        attempt = Attempt(
            number=number,
            candidate=candidate,
            self_reply=self_reply,
            self_review=self_review,
            deterministic_checks=checks,
            external_reply=external_reply,
            external_review=external_review,
            independent_passed=independent_passed,
        )
        attempts.append(attempt)

        emit("\nCriteria comparison:")
        emit("Criterion          | Self | Independent")
        emit("-------------------+------+------------")
        independent = {check.name: check.passed for check in checks}
        independent.update(external_review.criteria)
        for name in SELF_CRITERIA:
            self_label = "PASS" if self_review.criteria.get(name, False) else "FAIL"
            independent_label = "PASS" if independent.get(name, False) else "FAIL"
            emit(f"{name:<19}| {self_label:<5}| {independent_label}")

        if self_review.verdict and not independent_passed:
            false_positive_observed = True
            emit("FALSE POSITIVE OBSERVED: self-evaluation accepted a flawed update.")
        elif self_review.verdict and independent_passed:
            emit("AGREEMENT: both evaluation paths accepted this update.")
        elif not self_review.verdict and not independent_passed:
            emit("AGREEMENT: both evaluation paths found a problem.")
        else:
            emit("DISAGREEMENT: self-evaluation rejected an independently passing update.")

        if independent_passed:
            emit("Stop reason: every independent criterion passed.")
            pause()
            return _result(
                mode="external",
                attempts=attempts,
                stop_reason="all independent criteria passed",
                accepted=True,
                false_positive_observed=false_positive_observed,
            )
        if number == max_attempts:
            emit("Stop reason: the independent-evaluation attempt limit was reached.")
            pause()
            return _result(
                mode="external",
                attempts=attempts,
                stop_reason="independent-evaluation attempt limit reached",
                accepted=False,
                false_positive_observed=false_positive_observed,
            )

        failed_checks = [
            f"{check.name}: FAIL ({check.detail})"
            for check in checks
            if not check.passed
        ]
        feedback = "\n".join(failed_checks + [external_review.feedback])
        emit("\nIndependent feedback sent to the generator:")
        emit(feedback)
        pause()
        candidate = provider.revise(candidate, scenario, feedback)

    raise AssertionError("external-evaluation loop exited unexpectedly")
