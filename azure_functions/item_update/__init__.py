import json
import logging
from typing import Any, Dict

import azure.functions as func

from shared_code.data import update_item, init_database, create_sample_data
from shared_code.servicebus import publish_event

ALLOWED_FIELDS = {"status", "qty"}


def _sanitize(payload: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {key: value for key, value in payload.items() if key in ALLOWED_FIELDS}
    if "status" in sanitized:
        sanitized["status"] = str(sanitized["status"]).lower()
    return sanitized


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        list_id = req.route_params.get("list_id")
        item_id = req.route_params.get("item_id")
        
        if not list_id or not item_id:
            logging.warning("Missing list_id or item_id in route parameters")
            return func.HttpResponse(
                body=json.dumps({"error": "Missing list_id or item_id"}),
                status_code=400,
                mimetype="application/json",
            )
        
        logging.info("Updating item %s in list %s", item_id, list_id)

        try:
            payload = req.get_json()
        except ValueError:
            logging.warning("Invalid JSON in request body")
            return func.HttpResponse(
                body=json.dumps({"error": "Body must be valid JSON"}),
                status_code=400,
                mimetype="application/json",
            )

        update_fields = _sanitize(payload if isinstance(payload, dict) else {})
        if not update_fields:
            logging.warning("No valid fields to update in payload: %s", payload)
            return func.HttpResponse(
                body=json.dumps({"error": "No valid fields to update"}),
                status_code=400,
                mimetype="application/json",
            )

        # Initialize database and create sample data if needed
        try:
            init_database()
            create_sample_data()
        except Exception as e:
            logging.error("Database initialization failed: %s", str(e))
            return func.HttpResponse(
                body=json.dumps({"error": "Database not available"}),
                status_code=500,
                mimetype="application/json",
            )

        # Update item in database
        updated_item = update_item(list_id, item_id, update_fields)
        if updated_item is None:
            logging.warning("List %s or item %s not found", list_id, item_id)
            return func.HttpResponse(
                body=json.dumps({"error": "List or item not found"}),
                status_code=404,
                mimetype="application/json",
            )
        
        # Publish event (this will gracefully handle missing Service Bus)
        try:
            publish_event(
                {
                    "type": "item-updated",
                    "listId": list_id,
                    "itemId": item_id,
                    "changes": update_fields,
                    "version": updated_item["version"],
                }
            )
        except Exception as e:
            logging.warning("Failed to publish event: %s", str(e))
            # Don't fail the request if event publishing fails
        
        logging.info("Successfully updated item %s in list %s", item_id, list_id)
        return func.HttpResponse(body=json.dumps(updated_item), mimetype="application/json")
    
    except Exception as e:
        logging.exception("Error in item_update function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
