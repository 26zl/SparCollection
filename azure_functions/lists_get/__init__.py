import json
import logging

import azure.functions as func

from shared_code.database import get_lists


def main(req: func.HttpRequest) -> func.HttpResponse:
    shop_id = req.params.get("shopId")
    if not shop_id:
        return func.HttpResponse(
            body=json.dumps({"error": "shopId is required"}, ensure_ascii=False),
            status_code=400,
            mimetype="application/json",
        )

    logging.info("Fetching lists for shop %s", shop_id)

    try:
        lists = get_lists(shop_id)
    except Exception:
        logging.exception("Database error while fetching lists for shop %s", shop_id)
        return func.HttpResponse(
            body=json.dumps({"error": "database error"}, ensure_ascii=False),
            status_code=500,
            mimetype="application/json",
        )

    return func.HttpResponse(
        body=json.dumps(lists, ensure_ascii=False),
        mimetype="application/json",
    )
