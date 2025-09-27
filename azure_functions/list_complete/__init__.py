import json
import logging
from datetime import datetime, timezone

import azure.functions as func

from shared_code import load_json, persist_json, publish_event


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.route_params.get("list_id")
    logging.info("Completing list %s", list_id)

    payload = {}
    try:
        if req.get_body():
            payload = req.get_json()
    except ValueError:
        return func.HttpResponse(
            body=json.dumps({"error": "Body must be valid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    lists = load_json("lists.json")
    for shopping_list in lists:
        if shopping_list["id"] != list_id:
            continue
        shopping_list["status"] = "completed"
        shopping_list["completed_at"] = datetime.now(timezone.utc).isoformat()
        if isinstance(payload, dict) and payload.get("completed_by"):
            shopping_list["completed_by"] = str(payload["completed_by"])
        persist_json("lists.json", lists)
        publish_event(
            {
                "type": "list-completed",
                "listId": list_id,
                "status": shopping_list["status"],
                "completedAt": shopping_list["completed_at"],
                "completedBy": shopping_list.get("completed_by"),
            }
        )
        return func.HttpResponse(
            body=json.dumps({"queued": True, "listId": list_id}),
            mimetype="application/json",
        )

    return func.HttpResponse(
        body=json.dumps({"error": "List not found"}),
        status_code=404,
        mimetype="application/json",
    )
