import json
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        body=json.dumps({"message": "Azure Functions is working!", "status": "ok"}),
        mimetype="application/json"
    )
