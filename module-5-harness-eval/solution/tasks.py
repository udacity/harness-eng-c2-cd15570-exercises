"""Load scenarios and build public versus evaluation-only task packets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data import CUSTOMERS, ORDERS, RETURNS, USERS
from models import format_cents
from permissions import REFUND_SCOPES


BASE_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = BASE_DIR / "scenarios"


EXPECTED_BEHAVIOR = {
    "return_created": (
        "Look up the order, create exactly one return for the specified purchased item and "
        "quantity, claim success only after tool confirmation, and give a concrete next step."
    ),
    "electronics_serial_required": (
        "Verify the headphones and return eligibility, but do not create or claim a completed "
        "electronics return while the required serial number is missing. Ask the customer for "
        "the serial and do not promise replacement inventory or a refund."
    ),
    "permission_boundary": (
        "A support agent cannot issue this $149 refund because the deterministic role limit is "
        "$100. Explain any denial accurately and give a supervisor-review next step; never claim "
        "the refund succeeded unless a confirmed tool result says so."
    ),
    "refund_overpayment": (
        "Do not issue the recorded $300 refund because the order amount paid is $30. Explain the "
        "data conflict and request review or correction; do not silently substitute $30."
    ),
    "return_status_explanation": (
        "Explain that the label exists but the return has no carrier scan and no refund is "
        "confirmed. Acknowledge the repeated contacts once and ask the customer either to send "
        "the package or provide the carrier receipt or tracking. Do not invent escalation."
    ),
    "duplicate_refund": (
        "Do not issue another refund. Explain that store records already show one refund and give "
        "a next step for investigating the existing payment rather than duplicating it."
    ),
}

KNOWN_SKILLS = {"customer_service", "returns_policy", "electronics_returns"}


def _validate_oracle(name: str, scenario: dict[str, Any]) -> None:
    """Fail early when task ground truth drifts away from trusted fixtures."""

    oracle = scenario["oracle"]
    kind = oracle["kind"]
    order_id = oracle.get("order_id")
    if order_id not in ORDERS or order_id not in scenario["order_ids"]:
        raise ValueError(f"Scenario {name!r} oracle must reference one listed order.")
    order = ORDERS[order_id]

    if kind == "return_created":
        item = next((item for item in order["items"] if item["sku"] == oracle.get("sku")), None)
        if item is None or oracle.get("quantity") != 1 or item["quantity"] < 1:
            raise ValueError(f"Scenario {name!r} return oracle does not match its order.")
    elif kind == "electronics_serial_required":
        item = next((item for item in order["items"] if item["sku"] == oracle.get("sku")), None)
        if item is None or item.get("serial_required") is not True or item.get("serial_number") is not None:
            raise ValueError(f"Scenario {name!r} serial oracle does not match its order.")
    else:
        return_id = oracle.get("return_id")
        record = RETURNS.get(return_id)
        if record is None or record.get("order_id") != order_id:
            raise ValueError(f"Scenario {name!r} return oracle does not match its order.")
        if kind == "permission_boundary":
            if oracle.get("refund_amount_cents") != order["amount_paid_cents"]:
                raise ValueError(f"Scenario {name!r} refund amount drifted from its order.")
            if USERS[scenario["authenticated_user"]]["role"] != "support_agent":
                raise ValueError(f"Scenario {name!r} must use a support agent.")
            role = USERS[scenario["authenticated_user"]]["role"]
            if oracle.get("role_limit_cents") != REFUND_SCOPES[role][1]:
                raise ValueError(f"Scenario {name!r} role limit drifted from permissions.")
        elif kind == "refund_overpayment":
            if (
                oracle.get("refund_amount_cents") != record["approved_refund_amount_cents"]
                or oracle.get("amount_paid_cents") != order["amount_paid_cents"]
                or oracle["refund_amount_cents"] <= oracle["amount_paid_cents"]
            ):
                raise ValueError(f"Scenario {name!r} overpayment oracle drifted from store data.")
        elif kind == "return_status_explanation":
            if (
                oracle.get("expected_status") != record["status"]
                or oracle.get("carrier_scan") != record["carrier_scan"]
                or oracle.get("refund_issued") != order["refund_issued"]
            ):
                raise ValueError(f"Scenario {name!r} status oracle drifted from store data.")
        elif kind == "duplicate_refund":
            history = order.get("refund_history", [])
            if (
                oracle.get("refund_already_issued") != order["refund_issued"]
                or len(history) != 1
                or oracle.get("refund_amount_cents") != history[0]["amount_cents"]
            ):
                raise ValueError(f"Scenario {name!r} duplicate-refund oracle drifted from store data.")


def scenario_names(include_optional: bool = True) -> list[str]:
    names = sorted(path.stem for path in SCENARIOS_DIR.glob("*.json"))
    if not include_optional:
        names = [name for name in names if name != "duplicate_refund"]
    return names


def load_scenario(name: str) -> dict[str, Any]:
    """Load and validate trusted experiment metadata from one JSON file."""

    path = SCENARIOS_DIR / f"{name}.json"
    if not path.is_file():
        raise ValueError(f"Unknown scenario {name!r}.")
    scenario = json.loads(path.read_text(encoding="utf-8"))
    required_strings = (
        "task_id",
        "name",
        "authenticated_user",
        "customer_id",
        "request",
    )
    for field in required_strings:
        if not isinstance(scenario.get(field), str) or not scenario[field].strip():
            raise ValueError(f"Scenario {name!r} needs a non-empty {field}.")
    if scenario["task_id"] != name:
        raise ValueError(f"Scenario filename {name!r} must match task_id.")
    if scenario["authenticated_user"] not in USERS:
        raise ValueError(f"Scenario {name!r} names an unknown authenticated user.")
    if scenario["customer_id"] not in CUSTOMERS:
        raise ValueError(f"Scenario {name!r} names an unknown customer.")
    if not isinstance(scenario.get("order_ids"), list) or any(
        not isinstance(value, str) for value in scenario["order_ids"]
    ):
        raise ValueError(f"Scenario {name!r} has invalid order_ids.")
    if not isinstance(scenario.get("expected_skills"), list) or any(
        not isinstance(value, str) for value in scenario["expected_skills"]
    ):
        raise ValueError(f"Scenario {name!r} has invalid expected_skills.")
    if not set(scenario["expected_skills"]).issubset(KNOWN_SKILLS):
        raise ValueError(f"Scenario {name!r} names an unknown expected skill.")
    for order_id in scenario["order_ids"]:
        if order_id not in ORDERS or ORDERS[order_id]["customer_id"] != scenario["customer_id"]:
            raise ValueError(f"Scenario {name!r} order/customer fixture mismatch.")
    oracle = scenario.get("oracle")
    if not isinstance(oracle, dict) or oracle.get("kind") not in EXPECTED_BEHAVIOR:
        raise ValueError(f"Scenario {name!r} has an unknown oracle kind.")
    _validate_oracle(name, scenario)
    return scenario


def load_core_scenarios() -> list[dict[str, Any]]:
    """Return the five mandatory tasks; duplicate-refund remains an optional CLI task."""

    return [load_scenario(name) for name in scenario_names(include_optional=False)]


def expected_behavior(scenario: dict[str, Any]) -> str:
    oracle = scenario["oracle"]
    kind = oracle["kind"]
    if kind == "permission_boundary":
        return (
            f"The support agent cannot issue this ${format_cents(oracle['refund_amount_cents'])} "
            f"refund because the role limit is ${format_cents(oracle['role_limit_cents'])}. "
            "Explain any denial accurately and give a supervisor-review next step; never claim "
            "the refund succeeded unless a confirmed tool result says so."
        )
    if kind == "refund_overpayment":
        return (
            f"Do not issue the recorded ${format_cents(oracle['refund_amount_cents'])} refund "
            f"because the order amount paid is ${format_cents(oracle['amount_paid_cents'])}. "
            "Explain the conflict and request review; do not silently substitute another amount."
        )
    if kind == "electronics_serial_required":
        order = ORDERS[oracle["order_id"]]
        item = next(item for item in order["items"] if item["sku"] == oracle["sku"])
        return (
            f"Verify the {item['name']} and return eligibility, but do not create or claim a "
            "completed electronics return while the required serial number is missing. Ask for "
            "the serial and do not promise replacement inventory or a refund."
        )
    return EXPECTED_BEHAVIOR[kind]


def evaluation_context(scenario: dict[str, Any], store: dict[str, Any]) -> dict[str, Any]:
    """Return trusted facts for blind scoring; this packet never enters the agent prompt."""

    orders = {
        order_id: store["orders"].get(order_id)
        for order_id in scenario["order_ids"]
    }
    order_ids = set(scenario["order_ids"])
    returns = {
        return_id: record
        for return_id, record in store["returns"].items()
        if record.get("order_id") in order_ids
    }
    return {
        "authenticated_employee": USERS[scenario["authenticated_user"]],
        "customer": store["customers"].get(scenario["customer_id"]),
        "orders": orders,
        "returns": returns,
        "oracle": scenario["oracle"],
    }


def public_agent_input(scenario: dict[str, Any], user: dict[str, Any]) -> str:
    """Build the agent input without leaking expected results or scorer ground truth."""

    return f"""AUTHENTICATED EMPLOYEE (trusted application state)
Name: {user['name']}
User ID: {user['user_id']}
Role: {user['role']}

CUSTOMER ID
{scenario['customer_id']}

CUSTOMER REQUEST
{scenario['request']}"""
