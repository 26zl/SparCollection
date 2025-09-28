import json
import logging
import azure.functions as func

from shared_code.data import get_list, init_database, create_sample_data


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
        
        # Initialize database and create sample data if needed
        try:
            init_database()
            create_sample_data()
        except Exception as e:
            logging.warning("Database initialization failed: %s", str(e))
            return func.HttpResponse(
                body=json.dumps({"error": "Database not available"}),
                status_code=500,
                mimetype="application/json",
            )
        
        # Get list from database
        data = get_list(list_id, shop_id)
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
