import json
import logging
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.route_params.get("list_id")
    logging.info("Fetching list %s", list_id)
    lists = load_json("lists.json")
    data = next((entry for entry in lists if entry["id"] == list_id), None)
    if data is None:
        return func.HttpResponse(
            body=json.dumps({"error": "List not found"}),
            status_code=404,
            mimetype="application/json",
        )
    return func.HttpResponse(body=json.dumps(data), mimetype="application/json")
