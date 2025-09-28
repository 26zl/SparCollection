import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Test basic functionality
        return func.HttpResponse(
            body=json.dumps({
                "status": "ok",
                "message": "Azure Functions is working",
                "timestamp": "2025-09-28T03:25:00Z"
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({
                "error": "Internal server error",
                "details": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )
