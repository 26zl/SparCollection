import json
import logging
from typing import Any, Dict, List

import azure.functions as func

from shared_code.data import create_list
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


def _validate_title(title: Any) -> str:
    if not isinstance(title, str):
        raise ValueError("title must be a string")
    clean = title.strip()
    if not clean:
        raise ValueError("title is required")
    if len(clean) > 120:
        raise ValueError("title must be 120 characters or fewer")
    return clean


def _validate_items(items: Any) -> List[Dict[str, Any]]:
    if items is None:
        return []
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) > 500:
        raise ValueError("items cannot exceed 500 entries")

    validated: List[Dict[str, Any]] = []
    allowed_status = {"pending", "collected", "unavailable"}

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each item must be an object")

        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("each item requires a non-empty name")
        name_clean = name.strip()
        if len(name_clean) > 200:
            raise ValueError("item name must be 200 characters or fewer")

        qty = item.get("qty", 1)
        if not isinstance(qty, (int, float)) or int(qty) < 1:
            raise ValueError("qty must be a positive number")
        qty_int = int(qty)
        if qty_int > 10000:
            raise ValueError("qty must be 10,000 or less")

        status = item.get("status", "pending")
        if not isinstance(status, str) or status not in allowed_status:
            raise ValueError("status must be one of pending, collected, unavailable")

        sku = item.get("sku")
        if sku is not None:
            if not isinstance(sku, str):
                raise ValueError("sku must be a string")
            if len(sku) > 120:
                raise ValueError("sku must be 120 characters or fewer")

        validated.append(
            {
                "id": item.get("id"),
                "sku": sku,
                "name": name_clean,
                "qty": qty_int,
                "status": status,
            }
        )

    return validated


def main(req: func.HttpRequest) -> func.HttpResponse:
    shop_id = req.params.get("shopId")
    if not shop_id:
        return func.HttpResponse(
            body=json.dumps({"error": "shopId is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )
    if not isinstance(shop_id, str) or not shop_id.strip():
        return func.HttpResponse(
            body=json.dumps({"error": "shopId must be a non-empty string"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )
    shop_id = shop_id.strip()
    if len(shop_id) > 120:
        return func.HttpResponse(
            body=json.dumps({"error": "shopId must be 120 characters or fewer"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    logging.info("Creating new list for shop %s", shop_id)

    try:
        payload = _parse_payload(req.get_body())
    except ValueError as exc:
        return func.HttpResponse(
            body=json.dumps({"error": str(exc)}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    try:
        title = _validate_title(payload.get("title"))
        items = _validate_items(payload.get("items", []))
    except ValueError as exc:
        return func.HttpResponse(
            body=json.dumps({"error": str(exc)}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    logging.info("Creating new list for shop %s with %d items", shop_id, len(items))

    try:
        new_list = create_list(title, shop_id, items)
    except Exception:
        logging.exception("Database error while creating list for shop %s", shop_id)
        return func.HttpResponse(
            body=json.dumps({"error": "database error"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    try:
        publish_event(
            {
                "type": "list-created",
                "listId": new_list["id"],
                "title": new_list["title"],
                "shopId": shop_id,
                "itemCount": len(new_list["items"]),
            }
        )
    except Exception:
        logging.warning("Failed to publish list-created event for %s", new_list["id"])

    return func.HttpResponse(
        body=json.dumps(new_list, ensure_ascii=False),
        mimetype="application/json",
    )
