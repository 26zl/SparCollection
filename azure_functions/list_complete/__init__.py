import json
import logging
from datetime import datetime, timezone

import azure.functions as func

from shared_code.data import complete_list, init_database, create_sample_data
from shared_code.servicebus import publish_event


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        list_id = req.route_params.get("list_id")
        
        if not list_id:
            logging.warning("Missing list_id in route parameters")
            return func.HttpResponse(
                body=json.dumps({"error": "Missing list_id"}),
                status_code=400,
                mimetype="application/json",
            )
        
        logging.info("Completing list %s", list_id)

        payload = {}
        try:
            if req.get_body():
                payload = req.get_json()
        except ValueError:
            logging.warning("Invalid JSON in request body")
            return func.HttpResponse(
                body=json.dumps({"error": "Body must be valid JSON"}),
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

        # Complete list in database
        success = complete_list(list_id)
        if not success:
            logging.warning("List %s not found", list_id)
            return func.HttpResponse(
                body=json.dumps({"error": "List not found"}),
                status_code=404,
                mimetype="application/json",
            )
        
        # Publish event (this will gracefully handle missing Service Bus)
        try:
            completed_by = None
            if isinstance(payload, dict) and payload.get("completed_by"):
                completed_by = str(payload["completed_by"])
            
            publish_event(
                {
                    "type": "list-completed",
                    "listId": list_id,
                    "status": "completed",
                    "completedAt": datetime.now(timezone.utc).isoformat(),
                    "completedBy": completed_by,
                }
            )
        except Exception as e:
            logging.warning("Failed to publish event: %s", str(e))
            # Don't fail the request if event publishing fails
        
        logging.info("Successfully completed list %s", list_id)
        return func.HttpResponse(
            body=json.dumps({"queued": True, "listId": list_id}),
            mimetype="application/json",
        )
    
    except Exception as e:
        logging.exception("Error in list_complete function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
