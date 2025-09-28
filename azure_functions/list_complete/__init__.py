import json
import logging
from datetime import datetime, timezone

import azure.functions as func

from shared_code import load_json, persist_json, publish_event


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

        # Try to load data, fallback to empty list if file doesn't exist
        try:
            lists = load_json("lists.json")
        except FileNotFoundError:
            logging.warning("lists.json not found, returning 404")
            return func.HttpResponse(
                body=json.dumps({"error": "List not found"}),
                status_code=404,
                mimetype="application/json",
            )
        except Exception as e:
            logging.error("Error loading lists.json: %s", str(e))
            return func.HttpResponse(
                body=json.dumps({"error": "Internal server error"}),
                status_code=500,
                mimetype="application/json",
            )

        for shopping_list in lists:
            if shopping_list["id"] != list_id:
                continue
            
            # Update list status
            shopping_list["status"] = "completed"
            shopping_list["completed_at"] = datetime.now(timezone.utc).isoformat()
            if isinstance(payload, dict) and payload.get("completed_by"):
                shopping_list["completed_by"] = str(payload["completed_by"])
            
            # Save changes
            try:
                persist_json("lists.json", lists)
            except Exception as e:
                logging.error("Error saving lists.json: %s", str(e))
                return func.HttpResponse(
                    body=json.dumps({"error": "Failed to save changes"}),
                    status_code=500,
                    mimetype="application/json",
                )
            
            # Publish event (this will gracefully handle missing Service Bus)
            try:
                publish_event(
                    {
                        "type": "list-completed",
                        "listId": list_id,
                        "status": shopping_list["status"],
                        "completedAt": shopping_list["completed_at"],
                        "completedBy": shopping_list.get("completed_by"),
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

        logging.warning("List %s not found", list_id)
        return func.HttpResponse(
            body=json.dumps({"error": "List not found"}),
            status_code=404,
            mimetype="application/json",
        )
    
    except Exception as e:
        logging.exception("Error in list_complete function: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error", "details": str(e)}),
            status_code=500,
            mimetype="application/json",
        )
