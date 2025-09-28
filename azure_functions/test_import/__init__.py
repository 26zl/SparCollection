import json
import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Testing shared_code import")
    
    try:
        from shared_code.data import get_lists
        logging.info("Successfully imported get_lists")
        
        # Try to call the function
        try:
            lists = get_lists("NO-TR-001")
            logging.info("Successfully called get_lists")
            return func.HttpResponse(
                body=json.dumps({"message": "Import and function call successful", "lists_count": len(lists)}, ensure_ascii=False),
                mimetype="application/json",
                status_code=200,
            )
        except Exception as e:
            logging.exception("Error calling get_lists: %s", str(e))
            return func.HttpResponse(
                body=json.dumps({"message": "Import successful but function call failed", "error": str(e)}, ensure_ascii=False),
                mimetype="application/json",
                status_code=500,
            )
            
    except Exception as e:
        logging.exception("Error importing shared_code.data: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"message": "Import failed", "error": str(e)}, ensure_ascii=False),
            mimetype="application/json",
            status_code=500,
        )
