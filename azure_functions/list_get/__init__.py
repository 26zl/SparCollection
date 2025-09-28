import json
import logging
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        list_id = req.params.get("listId")
        if not list_id:
            logging.warning("Missing listId parameter")
            return func.HttpResponse(
                body=json.dumps({"error": "listId query parameter is required"}),
                status_code=400,
                mimetype="application/json",
            )
        shop_id = req.params.get("shopId")
        logging.info("Getting list %s for shop %s", list_id, shop_id)
        
        lists = load_json("lists.json")
        data = next(
            (
                entry
                for entry in lists
                if entry["id"] == list_id and (not shop_id or entry.get("shop_id") in (None, shop_id))
            ),
            None,
        )
        if data is None:
            logging.warning("List %s not found for shop %s", list_id, shop_id)
            return func.HttpResponse(
                body=json.dumps({"error": "List not found"}),
                status_code=404,
                mimetype="application/json",
            )
        return func.HttpResponse(body=json.dumps(data), mimetype="application/json")
    except Exception as e:
        logging.exception("Error in list_get function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )
