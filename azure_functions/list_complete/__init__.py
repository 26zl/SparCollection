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


def _validate_employee_id(employee_id: Any) -> str:
    if employee_id is None:
        return ""
    if not isinstance(employee_id, (str, int, float)):
        raise ValueError("employeeId must be a string or number")
    employee_str = str(employee_id).strip()
    if len(employee_str) > 120:
        raise ValueError("employeeId must be 120 characters or fewer")
    return employee_str


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

    shop_id_param = req.params.get("shopId")
    if shop_id_param:
        shop_id_param = shop_id_param.strip()
        if len(shop_id_param) > 120:
            return func.HttpResponse(
                body=json.dumps({"error": "shopId must be 120 characters or fewer"}, ensure_ascii=False),
                status_code=400,
                mimetype="application/json",
            )

    try:
        employee_id = _validate_employee_id(payload.get("employeeId") if isinstance(payload, dict) else None)
    except ValueError as exc:
        return func.HttpResponse(
            body=json.dumps({"error": str(exc)}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    try:
        result = complete_list(list_id, employee_id or None, shop_id_param)
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
        # Get the full list data for payment processing
        from shared_code.data import get_list
        shop_id = result.get("shopId") or result.get("shop_id") or shop_id_param
        full_list = get_list(list_id, shop_id) if shop_id else get_list(list_id)
        
        resolved_shop_id = shop_id or (full_list.get("shop_id") if full_list else None) or "unknown"
        resolved_title = (
            result.get("title")
            or (full_list.get("title") if full_list else None)
            or f"List {list_id}"
        )
        
        publish_event(
            {
                "type": "list-completed",
                "listId": list_id,
                "shopId": resolved_shop_id,
                "status": "COMPLETED",
                "completedAt": result.get("completedAt"),
                "completedBy": result.get("completedBy") or employee_id or "unknown",
                "items": full_list.get("items", []) if full_list else [],
                "title": resolved_title
            }
        )
    except Exception:
        logging.warning("Failed to publish list-completed event for %s", list_id)

    return func.HttpResponse(
        body=json.dumps(result, ensure_ascii=False),
        mimetype="application/json",
    )
