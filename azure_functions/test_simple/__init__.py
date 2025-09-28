import json
import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Test function called")
    
    return func.HttpResponse(
        body=json.dumps({"message": "Hello from Azure Functions!", "status": "working"}, ensure_ascii=False),
        mimetype="application/json",
        status_code=200,
    )
