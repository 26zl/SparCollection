import json
import logging

import azure.functions as func

from shared_code.db import fetch_list_with_items


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.params.get("listId")
    if not list_id:
        return func.HttpResponse(
            body=json.dumps({"error": "listId is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    shop_id = req.params.get("shopId")
    logging.info("Fetching list %s (shop %s)", list_id, shop_id)

    try:
        data = fetch_list_with_items(list_id, shop_id)
    except Exception:
        logging.exception("Database error while fetching list %s", list_id)
        return func.HttpResponse(
            body=json.dumps({"error": "database error"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    if data is None:
        return func.HttpResponse(
            body=json.dumps({"error": "List not found"}, ensure_ascii=False),
            status_code=404,
            mimetype="application/json",
        )

    return func.HttpResponse(
        body=json.dumps(data, ensure_ascii=False),
        mimetype="application/json",
    )
