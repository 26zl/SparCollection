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


def main(req: func.HttpRequest) -> func.HttpResponse:
    shop_id = req.params.get("shopId")
    if not shop_id:
        return func.HttpResponse(
            body=json.dumps({"error": "shopId is required"}, ensure_ascii=False),
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

    title = payload.get("title")
    if not title:
        return func.HttpResponse(
            body=json.dumps({"error": "title is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    items = payload.get("items", [])
    if not isinstance(items, list):
        return func.HttpResponse(
            body=json.dumps({"error": "items must be a list"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

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
