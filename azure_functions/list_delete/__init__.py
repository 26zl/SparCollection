import json
import logging

import azure.functions as func

from shared_code.data import delete_list
from shared_code.servicebus import publish_event


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.route_params.get("list_id")
    if not list_id:
        return func.HttpResponse(
            body=json.dumps({"error": "list_id is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    shop_id = req.params.get("shopId")
    logging.info("Deleting list %s (shop %s)", list_id, shop_id)

    try:
        success = delete_list(list_id, shop_id)
    except Exception:
        logging.exception("Database error while deleting list %s", list_id)
        return func.HttpResponse(
            body=json.dumps({"error": "database error"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    if not success:
        return func.HttpResponse(
            body=json.dumps({"error": "List not found"}, ensure_ascii=False),
            status_code=404,
            mimetype="application/json",
        )

    try:
        publish_event(
            {
                "type": "list-deleted",
                "listId": list_id,
                "shopId": shop_id,
            }
        )
    except Exception:
        logging.warning("Failed to publish list-deleted event for %s", list_id)

    return func.HttpResponse(
        body=json.dumps({"message": "List deleted successfully"}, ensure_ascii=False),
        mimetype="application/json",
    )
