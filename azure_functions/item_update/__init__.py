import json
import logging
from typing import Any, Dict

import azure.functions as func

from shared_code import load_json, persist_json

ALLOWED_FIELDS = {"status", "qty"}


def _sanitize(payload: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {key: value for key, value in payload.items() if key in ALLOWED_FIELDS}
    if "status" in sanitized:
        sanitized["status"] = str(sanitized["status"]).lower()
    return sanitized


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.route_params.get("list_id")
    item_id = req.route_params.get("item_id")
    logging.info("Updating item %s in list %s", item_id, list_id)

    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse(
            body=json.dumps({"error": "Body must be valid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    update_fields = _sanitize(payload if isinstance(payload, dict) else {})
    if not update_fields:
        return func.HttpResponse(
            body=json.dumps({"error": "No valid fields to update"}),
            status_code=400,
            mimetype="application/json",
        )

    lists = load_json("lists.json")
    for shopping_list in lists:
        if shopping_list["id"] != list_id:
            continue
        for item in shopping_list.get("items", []):
            if item["id"] != item_id:
                continue
            item.update(update_fields)
            item["version"] = int(item.get("version", 0)) + 1
            persist_json("lists.json", lists)
            return func.HttpResponse(body=json.dumps(item), mimetype="application/json")

    return func.HttpResponse(
        body=json.dumps({"error": "List or item not found"}),
        status_code=404,
        mimetype="application/json",
    )
