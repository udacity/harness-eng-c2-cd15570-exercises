"""Trusted identities and pristine incident state for each run."""

from copy import deepcopy


USERS = {
    "support_sam": {
        "user_id": "OPS-101",
        "name": "Sam Rivera",
        "role": "support_engineer",
    },
    "support_riley": {
        "user_id": "OPS-102",
        "name": "Riley Chen",
        "role": "support_engineer",
    },
    "responder_jordan": {
        "user_id": "OPS-201",
        "name": "Jordan Lee",
        "role": "responder",
    },
    "commander_morgan": {
        "user_id": "OPS-301",
        "name": "Morgan Chen",
        "role": "incident_commander",
    },
    "admin_taylor": {
        "user_id": "OPS-401",
        "name": "Taylor Smith",
        "role": "administrator",
    },
}


BASE_INCIDENT = {
    "incident_id": "INC-2048",
    "environment": "production",
    "service": "checkout-api",
    "assigned_user_id": "OPS-101",
    "incident_status": "INVESTIGATING",
    "service_health": "DEGRADED",
    "checkout_error_rate_percent": 18,
    "current_deployment": "checkout-v42",
    "last_known_good_deployment": "checkout-v41",
    "rollback_performed": False,
    "restart_performed": False,
    "recovery_confirmed": False,
    "deployment_history": [
        {"version": "checkout-v42", "current": True, "last_known_good": False},
        {"version": "checkout-v41", "current": False, "last_known_good": True},
        {"version": "checkout-v40", "current": False, "last_known_good": False},
    ],
    "logs": [
        "checkout request failures increased after checkout-v42 deployment",
        "payment dependency timeouts observed; root cause not confirmed",
    ],
    "actions": [],
}


def fresh_incident() -> dict:
    """Return isolated trusted incident state for one run."""

    return deepcopy(BASE_INCIDENT)
