import json
import logging

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Testing database connection...')
    
    try:
        from shared_code.data import get_lists, HAS_DATABASE
        logging.info(f'HAS_DATABASE = {HAS_DATABASE}')
        
        if HAS_DATABASE:
            logging.info('Attempting to get lists from database...')
            lists = get_lists("NO-TR-001")
            logging.info(f'Got {len(lists)} lists from database')
            return func.HttpResponse(
                json.dumps({"message": "Database connection successful", "lists_count": len(lists), "has_database": HAS_DATABASE}),
                mimetype="application/json",
                status_code=200
            )
        else:
            logging.warning('HAS_DATABASE is False, using fallback')
            return func.HttpResponse(
                json.dumps({"message": "Using fallback data", "has_database": HAS_DATABASE}),
                mimetype="application/json",
                status_code=200
            )
            
    except Exception as e:
        logging.error(f"Error testing database: {e}")
        return func.HttpResponse(
            json.dumps({"message": "Error", "error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
