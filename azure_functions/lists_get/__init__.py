import json
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    shop_id = req.params.get("shopId")
    lists = load_json("lists.json")
    if shop_id:
        lists = [entry for entry in lists if entry.get("shop_id") in (None, shop_id)]
    return func.HttpResponse(body=json.dumps(lists), mimetype="application/json")
