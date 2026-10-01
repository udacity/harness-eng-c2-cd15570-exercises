"""Simulated incident tools with no hook or authorization policy."""


def get_incident(incident: dict) -> dict:
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "environment": incident["environment"],
        "service": incident["service"],
        "incident_status": incident["incident_status"],
        "current_deployment": incident["current_deployment"],
    }


def get_service_health(incident: dict) -> dict:
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "service": incident["service"],
        "service_health": incident["service_health"],
        "checkout_error_rate_percent": incident["checkout_error_rate_percent"],
        "recovery_confirmed": incident["recovery_confirmed"],
    }


def get_deployment_history(incident: dict) -> dict:
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "deployments": incident["deployment_history"],
    }


def query_service_logs(incident: dict) -> dict:
    return {
        "status": "found",
        "incident_id": incident["incident_id"],
        "entries": incident["logs"],
    }


def rollback_deployment(incident: dict, target_version: str) -> dict:
    """Mutate deployment state without validating whether the target is safe."""

    previous = incident["current_deployment"]
    incident["current_deployment"] = target_version
    incident["rollback_performed"] = True
    for deployment in incident["deployment_history"]:
        deployment["current"] = deployment.get("version") == target_version
    action = {
        "tool": "rollback_deployment",
        "from_version": previous,
        "target_version": target_version,
    }
    incident["actions"].append(action)
    return {"status": "rolled_back", "incident_id": incident["incident_id"], **action}


def update_incident_status(incident: dict, status: str) -> dict:
    """Mutate incident status without deciding whether the transition is valid."""

    previous = incident["incident_status"]
    incident["incident_status"] = status
    action = {
        "tool": "update_incident_status",
        "previous_status": previous,
        "new_status": status,
    }
    incident["actions"].append(action)
    return {"status": "updated", "incident_id": incident["incident_id"], **action}
