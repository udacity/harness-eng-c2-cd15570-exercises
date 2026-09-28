"""Simulated permit tools. Authorization deliberately lives elsewhere."""

from typing import Any, Callable


APPLICATION_ID_PARAMETERS = {
    "type": "object",
    "properties": {"application_id": {"type": "string"}},
    "required": ["application_id"],
    "additionalProperties": False,
}


TOOLS = [
    {
        "type": "function",
        "name": "create_application",
        "description": "Create a new draft permit application for the authenticated user.",
        "parameters": {
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "address": {"type": "string"},
            },
            "required": ["project", "address"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "read_application",
        "description": "Read a permit application by ID.",
        "parameters": APPLICATION_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "edit_application",
        "description": "Change the project description on an existing application.",
        "parameters": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string"},
                "project": {"type": "string"},
            },
            "required": ["application_id", "project"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "submit_application",
        "description": "Submit a draft permit application.",
        "parameters": APPLICATION_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "request_corrections",
        "description": "Request corrections to a permit application.",
        "parameters": {
            "type": "object",
            "properties": {
                "application_id": {"type": "string"},
                "corrections": {"type": "string"},
            },
            "required": ["application_id", "corrections"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "approve_application",
        "description": "Approve a permit application.",
        "parameters": APPLICATION_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "reject_application",
        "description": "Reject a permit application.",
        "parameters": APPLICATION_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "issue_permit",
        "description": "Issue a permit for an application.",
        "parameters": APPLICATION_ID_PARAMETERS,
    },
    {
        "type": "function",
        "name": "revoke_permit",
        "description": "Revoke an issued permit.",
        "parameters": APPLICATION_ID_PARAMETERS,
    },
]


def _exact_arguments(arguments: dict, required: set[str]) -> None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object.")
    missing = required - arguments.keys()
    unexpected = arguments.keys() - required
    if missing:
        raise ValueError(f"Missing required arguments: {', '.join(sorted(missing))}.")
    if unexpected:
        raise ValueError(f"Unexpected arguments: {', '.join(sorted(unexpected))}.")
    for name in required:
        if not isinstance(arguments[name], str) or not arguments[name].strip():
            raise ValueError(f"{name} must be a nonempty string.")


def _application(arguments: dict, applications: dict[str, dict]) -> dict:
    application_id = arguments["application_id"]
    try:
        return applications[application_id]
    except KeyError as error:
        raise ValueError(f"Unknown application: {application_id}.") from error


def _next_application_id(applications: dict[str, dict]) -> str:
    number = 4000
    while f"P-{number}" in applications:
        number += 1
    return f"P-{number}"


def _create(arguments: dict, applications: dict[str, dict], user: dict) -> dict:
    _exact_arguments(arguments, {"project", "address"})
    application_id = _next_application_id(applications)
    applications[application_id] = {
        "application_id": application_id,
        "project": arguments["project"].strip(),
        "address": arguments["address"].strip(),
        "owner_user_id": user["user_id"],
        "status": "DRAFT",
        "corrections": None,
    }
    return {"status": "success", "application_id": application_id, "new_status": "DRAFT"}


def _read(arguments: dict, applications: dict[str, dict], user: dict) -> dict:
    _exact_arguments(arguments, {"application_id"})
    return {"status": "success", "application": dict(_application(arguments, applications))}


def _edit(arguments: dict, applications: dict[str, dict], user: dict) -> dict:
    _exact_arguments(arguments, {"application_id", "project"})
    application = _application(arguments, applications)
    application["project"] = arguments["project"].strip()
    return {
        "status": "success",
        "application_id": application["application_id"],
        "project": application["project"],
        "new_status": application["status"],
    }


def _set_status(new_status: str) -> Callable[[dict, dict[str, dict], dict], dict]:
    def handler(arguments: dict, applications: dict[str, dict], user: dict) -> dict:
        _exact_arguments(arguments, {"application_id"})
        application = _application(arguments, applications)
        application["status"] = new_status
        return {
            "status": "success",
            "application_id": application["application_id"],
            "new_status": new_status,
        }

    return handler


def _request_corrections(arguments: dict, applications: dict[str, dict], user: dict) -> dict:
    _exact_arguments(arguments, {"application_id", "corrections"})
    application = _application(arguments, applications)
    application["status"] = "CORRECTIONS_REQUESTED"
    application["corrections"] = arguments["corrections"].strip()
    return {
        "status": "success",
        "application_id": application["application_id"],
        "new_status": "CORRECTIONS_REQUESTED",
        "corrections": application["corrections"],
    }


TOOL_HANDLERS: dict[str, Callable[[dict, dict[str, dict], dict], dict]] = {
    "create_application": _create,
    "read_application": _read,
    "edit_application": _edit,
    "submit_application": _set_status("SUBMITTED"),
    "request_corrections": _request_corrections,
    "approve_application": _set_status("APPROVED"),
    "reject_application": _set_status("REJECTED"),
    "issue_permit": _set_status("PERMIT_ISSUED"),
    "revoke_permit": _set_status("REVOKED"),
}


assert {tool["name"] for tool in TOOLS} == set(TOOL_HANDLERS)


def execute_tool(
    tool_name: str,
    arguments: dict,
    applications: dict[str, dict],
    authenticated_user: dict,
) -> dict[str, Any]:
    """Dispatch an allowlisted tool without performing authorization."""

    try:
        handler = TOOL_HANDLERS[tool_name]
    except KeyError as error:
        raise ValueError(f"Unsupported tool: {tool_name}.") from error
    return handler(arguments, applications, authenticated_user)
