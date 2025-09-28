import json
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    list_id = req.params.get("listId")
    if not list_id:
        return func.HttpResponse(
            body=json.dumps({"error": "listId query parameter is required"}),
            status_code=400,
            mimetype="application/json",
        )
    shop_id = req.params.get("shopId")
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
        return func.HttpResponse(
            body=json.dumps({"error": "List not found"}),
            status_code=404,
            mimetype="application/json",
        )
    return func.HttpResponse(body=json.dumps(data), mimetype="application/json")
