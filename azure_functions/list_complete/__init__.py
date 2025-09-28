import json
import logging
from typing import Any, Dict

import azure.functions as func

from shared_code.data import complete_list
from shared_code.servicebus import publish_event


def _parse_body(body: bytes) -> Dict[str, Any]:
    if not body:
        return {}
    try:
        payload = json.loads(body)
    except ValueError:
        raise ValueError("Body must be valid JSON")
    if not isinstance(payload, dict):
        raise ValueError("Body must be a JSON object")
    return payload


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.route_params.get("list_id")

    if not list_id:
        return func.HttpResponse(
            body=json.dumps({"error": "list_id is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    logging.info("Completing list %s", list_id)

    try:
        payload = _parse_body(req.get_body())
    except ValueError as exc:
        return func.HttpResponse(
            body=json.dumps({"error": str(exc)}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    employee_id = payload.get("employeeId") if isinstance(payload, dict) else None
    if employee_id is not None:
        employee_id = str(employee_id)

    try:
        result = complete_list(list_id, employee_id)
    except Exception:
        logging.exception("Database error while completing list %s", list_id)
        return func.HttpResponse(
            body=json.dumps({"error": "database error"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    if result is None:
        return func.HttpResponse(
            body=json.dumps({"error": "not found"}, ensure_ascii=False),
            status_code=404,
            mimetype="application/json",
        )

    try:
        publish_event(
            {
                "type": "list-completed",
                "listId": list_id,
                "status": "COMPLETED",
                "completedAt": result.get("completedAt"),
                "completedBy": result.get("completedBy"),
            }
        )
    except Exception:
        logging.warning("Failed to publish list-completed event for %s", list_id)

    return func.HttpResponse(
        body=json.dumps(result, ensure_ascii=False),
        mimetype="application/json",
    )
