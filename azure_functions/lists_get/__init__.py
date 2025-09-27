import json
import logging
import azure.functions as func

from shared_code import load_json


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Fetching all lists")
    lists = load_json("lists.json")
    return func.HttpResponse(body=json.dumps(lists), mimetype="application/json")
