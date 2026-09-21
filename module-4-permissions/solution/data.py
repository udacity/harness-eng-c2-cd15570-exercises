"""Trusted identities and fictional construction permit applications."""

from copy import deepcopy


USERS = {
    "contractor_alex": {
        "user_id": "USR-101",
        "name": "Alex Rivera",
        "role": "contractor",
    },
    "reviewer_jordan": {
        "user_id": "USR-201",
        "name": "Jordan Lee",
        "role": "reviewer",
    },
    "supervisor_morgan": {
        "user_id": "USR-301",
        "name": "Morgan Chen",
        "role": "supervisor",
    },
    "admin_taylor": {
        "user_id": "USR-401",
        "name": "Taylor Smith",
        "role": "administrator",
    },
}


BASE_APPLICATIONS = {
    "P-1042": {
        "application_id": "P-1042",
        "project": "Kitchen Addition",
        "address": "125 Oak Street",
        "owner_user_id": "USR-101",
        "status": "SUBMITTED",
        "corrections": None,
    },
    "P-2095": {
        "application_id": "P-2095",
        "project": "Detached Garage",
        "address": "88 Pine Avenue",
        "owner_user_id": "USR-999",
        "status": "DRAFT",
        "corrections": None,
    },
    "P-3100": {
        "application_id": "P-3100",
        "project": "Front Porch Replacement",
        "address": "41 Cedar Lane",
        "owner_user_id": "USR-777",
        "status": "APPROVED",
        "corrections": None,
    },
}


def fresh_applications() -> dict[str, dict]:
    """Return isolated application state for one run."""

    return deepcopy(BASE_APPLICATIONS)
