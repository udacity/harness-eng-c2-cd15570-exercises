"""Simulated store tools. Authorization and hooks deliberately live elsewhere."""

from copy import deepcopy
from typing import Any, Callable

from models import format_cents, money_to_cents


ORDER_ID_PARAMETERS = {
    "type": "object",
    "properties": {"order_id": {"type": "string"}},
    "required": ["order_id"],
    "additionalProperties": False,
}


BUSINESS_TOOLS = [
    {
        "type": "function",
        "name": "lookup_order",
        "description": "Look up a fictional order and its purchased items, return IDs, and refund status.",
        "parameters": ORDER_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "create_return",
        "description": "Create a return for a quantity of one SKU from an order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "sku": {"type": "string"},
                "quantity": {"type": "integer", "minimum": 1},
                "reason": {"type": "string"},
                "serial_number": {"type": "string"},
            },
            "required": ["order_id", "sku", "quantity"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "issue_refund",
        "description": "Issue a dollar refund to the original payment method for an order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "refund_amount": {"type": "number"},
            },
            "required": ["order_id", "refund_amount"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "issue_store_credit",
        "description": "Issue a positive dollar amount of store credit for an order.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "credit_amount": {"type": "number", "exclusiveMinimum": 0},
            },
            "required": ["order_id", "credit_amount"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "update_return",
        "description": "Update the status of an existing return.",
        "parameters": {
            "type": "object",
            "properties": {
                "return_id": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["LABEL_CREATED", "IN_TRANSIT", "RECEIVED", "CLOSED"],
                },
                "note": {"type": "string"},
            },
            "required": ["return_id", "status"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_return_status",
        "description": "Read the current status and known shipping facts for a return.",
        "parameters": {
            "type": "object",
            "properties": {"return_id": {"type": "string"}},
            "required": ["return_id"],
            "additionalProperties": False,
        },
    },
]

# Keep the short name used by the earlier course modules.
TOOLS = BUSINESS_TOOLS


def _arguments(arguments: dict, required: set[str], optional: set[str] | None = None) -> None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object.")
    optional = optional or set()
    missing = required - arguments.keys()
    unexpected = arguments.keys() - required - optional
    if missing:
        raise ValueError(f"Missing required arguments: {', '.join(sorted(missing))}.")
    if unexpected:
        raise ValueError(f"Unexpected arguments: {', '.join(sorted(unexpected))}.")


def _nonempty_string(arguments: dict, name: str) -> str:
    value = arguments.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string.")
    return value.strip()


def _order(store: dict, order_id: str) -> dict:
    try:
        return store["orders"][order_id]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Unknown order: {order_id}.") from error


def _return(store: dict, return_id: str) -> dict:
    try:
        return store["returns"][return_id]
    except (KeyError, TypeError) as error:
        raise ValueError(f"Unknown return: {return_id}.") from error


def _public_order(order: dict) -> dict:
    public = deepcopy(order)
    public["amount_paid"] = format_cents(public["amount_paid_cents"])
    for item in public["items"]:
        item["unit_price"] = format_cents(item["unit_price_cents"])
    for refund in public["refund_history"]:
        refund["amount"] = format_cents(refund["amount_cents"])
    return public


def _public_return(return_record: dict) -> dict:
    public = deepcopy(return_record)
    approved = public.get("approved_refund_amount_cents")
    public["approved_refund_amount"] = None if approved is None else format_cents(approved)
    return public


def lookup_order(arguments: dict, store: dict) -> dict:
    _arguments(arguments, {"order_id"})
    order_id = _nonempty_string(arguments, "order_id")
    return {"status": "success", "order": _public_order(_order(store, order_id))}


def create_return(arguments: dict, store: dict) -> dict:
    _arguments(arguments, {"order_id", "sku", "quantity"}, {"reason", "serial_number"})
    order_id = _nonempty_string(arguments, "order_id")
    sku = _nonempty_string(arguments, "sku")
    quantity = arguments["quantity"]
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("quantity must be a positive integer.")
    order = _order(store, order_id)
    if not any(item["sku"] == sku for item in order["items"]):
        raise ValueError(f"SKU {sku!r} is not part of order {order_id}.")

    reason = arguments.get("reason", "Customer requested a return.")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("reason must be a nonempty string when supplied.")
    serial_number = arguments.get("serial_number")
    if serial_number is not None and (not isinstance(serial_number, str) or not serial_number.strip()):
        raise ValueError("serial_number must be a nonempty string when supplied.")

    number = store["next_return_number"]
    return_id = f"RET-{number}"
    while return_id in store["returns"]:
        number += 1
        return_id = f"RET-{number}"
    store["next_return_number"] = number + 1
    record = {
        "return_id": return_id,
        "order_id": order_id,
        "sku": sku,
        "quantity": quantity,
        "reason": reason.strip(),
        "status": "LABEL_CREATED",
        "approved_refund_amount_cents": None,
        "carrier_scan": False,
        "prior_support_contacts": 0,
    }
    if serial_number is not None:
        record["serial_number"] = serial_number.strip()
    store["returns"][return_id] = record
    order["return_ids"].append(return_id)
    return {
        "status": "success",
        "return_id": return_id,
        "order_id": order_id,
        "new_status": "LABEL_CREATED",
    }


def issue_refund(arguments: dict, store: dict) -> dict:
    """Perform a refund without policy, duplicate, or permission checks."""

    _arguments(arguments, {"order_id", "refund_amount"})
    order_id = _nonempty_string(arguments, "order_id")
    amount_cents = money_to_cents(arguments["refund_amount"])
    order = _order(store, order_id)
    order["refund_issued"] = True
    order["refund_history"].append(
        {"amount_cents": amount_cents, "method": "original_payment"}
    )
    for return_id in order["return_ids"]:
        store["returns"][return_id]["status"] = "REFUNDED"
    return {
        "status": "success",
        "order_id": order_id,
        "refund_amount": format_cents(amount_cents),
        "refund_amount_cents": amount_cents,
        "refund_count": len(order["refund_history"]),
    }


def issue_store_credit(arguments: dict, store: dict) -> dict:
    _arguments(arguments, {"order_id", "credit_amount"})
    order_id = _nonempty_string(arguments, "order_id")
    amount_cents = money_to_cents(arguments["credit_amount"])
    if amount_cents <= 0:
        raise ValueError("credit_amount must be greater than zero.")
    _order(store, order_id)
    credit_id = f"CREDIT-{len(store['store_credits']) + 1:04d}"
    store["store_credits"].append(
        {"credit_id": credit_id, "order_id": order_id, "amount_cents": amount_cents}
    )
    return {
        "status": "success",
        "credit_id": credit_id,
        "order_id": order_id,
        "credit_amount": format_cents(amount_cents),
        "credit_amount_cents": amount_cents,
    }


def update_return(arguments: dict, store: dict) -> dict:
    _arguments(arguments, {"return_id", "status"}, {"note"})
    return_id = _nonempty_string(arguments, "return_id")
    new_status = _nonempty_string(arguments, "status")
    # REFUNDED is set only by issue_refund so return updates cannot impersonate
    # a money movement or bypass the refund boundaries.
    allowed_statuses = {"LABEL_CREATED", "IN_TRANSIT", "RECEIVED", "CLOSED"}
    if new_status not in allowed_statuses:
        raise ValueError(f"Unsupported return status: {new_status}.")
    record = _return(store, return_id)
    record["status"] = new_status
    if "note" in arguments:
        record["note"] = _nonempty_string(arguments, "note")
    return {"status": "success", "return_id": return_id, "new_status": new_status}


def get_return_status(arguments: dict, store: dict) -> dict:
    _arguments(arguments, {"return_id"})
    return_id = _nonempty_string(arguments, "return_id")
    return {"status": "success", "return": _public_return(_return(store, return_id))}


ToolHandler = Callable[[dict, dict], dict]

TOOL_HANDLERS: dict[str, ToolHandler] = {
    "lookup_order": lookup_order,
    "create_return": create_return,
    "issue_refund": issue_refund,
    "issue_store_credit": issue_store_credit,
    "update_return": update_return,
    "get_return_status": get_return_status,
}


assert {tool["name"] for tool in BUSINESS_TOOLS} == set(TOOL_HANDLERS)


def execute_tool(tool_name: str, arguments: dict, store: dict) -> dict[str, Any]:
    """Dispatch one allowlisted business tool without authorization or hooks."""

    try:
        handler = TOOL_HANDLERS[tool_name]
    except KeyError as error:
        raise ValueError(f"Unsupported tool: {tool_name}.") from error
    return handler(arguments, store)
