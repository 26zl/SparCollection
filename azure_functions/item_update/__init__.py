import json
import logging
from typing import Any, Dict, Optional

import azure.functions as func

from shared_code.db import update_item
from shared_code.servicebus import publish_event


def _parse_payload(body: bytes) -> Dict[str, Any]:
    if not body:
        return {}
    try:
        payload = json.loads(body)
    except ValueError:
        raise ValueError("Body must be valid JSON")
    if not isinstance(payload, dict):
        raise ValueError("Body must be a JSON object")
    return payload


def _normalize_qty(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.strip():
        return int(value)
    raise ValueError("qtyCollected must be a number")


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.route_params.get("list_id")
    item_id = req.route_params.get("item_id")

    if not list_id or not item_id:
        return func.HttpResponse(
            body=json.dumps({"error": "list_id and item_id are required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    logging.info("Updating item %s in list %s", item_id, list_id)

    try:
        payload = _parse_payload(req.get_body())
    except ValueError as exc:
        return func.HttpResponse(
            body=json.dumps({"error": str(exc)}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    status = payload.get("status")
    if not status:
        return func.HttpResponse(
            body=json.dumps({"error": "status is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    qty_collected: Optional[int] = None
    if "qtyCollected" in payload:
        try:
            qty_collected = _normalize_qty(payload.get("qtyCollected"))
        except ValueError as exc:
            return func.HttpResponse(
                body=json.dumps({"error": str(exc)}, ensure_ascii=False),
                status_code=400,
                mimetype="application/json",
            )

    try:
        updated_item = update_item(list_id, item_id, str(status), qty_collected)
    except Exception:
        logging.exception("Database error while updating item %s in list %s", item_id, list_id)
        return func.HttpResponse(
            body=json.dumps({"error": "database error"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    if updated_item is None:
        return func.HttpResponse(
            body=json.dumps({"error": "not found"}, ensure_ascii=False),
            status_code=404,
            mimetype="application/json",
        )

    changes = {"status": status}
    if qty_collected is not None:
        changes["qtyCollected"] = qty_collected

    try:
        publish_event(
            {
                "type": "item-updated",
                "listId": list_id,
                "itemId": item_id,
                "changes": changes,
                "version": updated_item.get("version"),
            }
        )
    except Exception:
        logging.warning("Failed to publish item-updated event for %s/%s", list_id, item_id)

    return func.HttpResponse(
        body=json.dumps(updated_item, ensure_ascii=False),
        mimetype="application/json",
    )
