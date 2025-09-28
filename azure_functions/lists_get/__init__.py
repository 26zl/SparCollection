import json
import logging
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        shop_id = req.params.get("shopId")
        logging.info("Getting lists for shop %s", shop_id)
        
        lists = load_json("lists.json")
        if shop_id:
            lists = [entry for entry in lists if entry.get("shop_id") in (None, shop_id)]
        
        logging.info("Found %d lists for shop %s", len(lists), shop_id)
        return func.HttpResponse(body=json.dumps(lists), mimetype="application/json")
    except Exception as e:
        logging.exception("Error in lists_get function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )
