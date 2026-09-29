"""Shared incident-update generator used by all three loops."""

from typing import Any

from harness.models import Scenario
from harness.scenario import authoritative_context, requirements_context


GENERATOR_INSTRUCTIONS = """
You are an incident-response communications assistant. Draft an accurate update
using only the authoritative incident facts. Distinguish confirmed facts from
hypotheses, do not claim an action or recovery that has not occurred, and give
a useful next diagnostic step. Return only the incident update.
""".strip()

REVISION_INSTRUCTIONS = """
You are an incident-response communications assistant. Revise the previous
update using the evaluator's feedback and authoritative facts. Correct every
identified problem. Return only the revised incident update.
""".strip()


def build_generation_prompt(scenario: Scenario) -> str:
    return f"""
Write a stakeholder update for this incident.

AUTHORITATIVE INCIDENT FACTS
{authoritative_context(scenario)}

OPERATOR REQUEST
{scenario.request}

RESPONSE REQUIREMENTS
{requirements_context(scenario)}

Return only the incident update.
""".strip()


def generate_initial_response(client: Any, model: str, scenario: Scenario) -> Any:
    """Start a fresh generator conversation."""

    return client.responses.create(
        model=model,
        instructions=GENERATOR_INSTRUCTIONS,
        input=build_generation_prompt(scenario),
    )
