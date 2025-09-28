import json
import logging
import azure.functions as func

from shared_code.database import get_lists, init_database, create_sample_data


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        shop_id = req.params.get("shopId")
        logging.info("Getting lists for shop %s", shop_id)
        
        # Initialize database and create sample data if needed
        try:
            init_database()
            create_sample_data()
        except Exception as e:
            logging.warning("Database initialization failed: %s", str(e))
            # Fallback to empty list if database is not available
            return func.HttpResponse(body=json.dumps([]), mimetype="application/json")
        
        # Get lists from database
        lists = get_lists(shop_id)
        
        logging.info("Found %d lists for shop %s", len(lists), shop_id)
        return func.HttpResponse(body=json.dumps(lists), mimetype="application/json")
    except Exception as e:
        logging.exception("Error in lists_get function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
