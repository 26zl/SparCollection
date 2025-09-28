import json
import logging
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        shop_id = req.params.get("shopId")
        logging.info("Getting lists for shop %s", shop_id)
        
        # Try to load data, fallback to empty list if file doesn't exist
        try:
            lists = load_json("lists.json")
        except FileNotFoundError:
            logging.warning("lists.json not found, returning empty list")
            lists = []
        except Exception as e:
            logging.error("Error loading lists.json: %s", str(e))
            lists = []
        
        if shop_id:
            lists = [entry for entry in lists if entry.get("shop_id") in (None, shop_id)]
        
        logging.info("Found %d lists for shop %s", len(lists), shop_id)
        return func.HttpResponse(body=json.dumps(lists), mimetype="application/json")
    except Exception as e:
        logging.exception("Error in lists_get function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
