import json
import logging
import os
import sys

import azure.functions as func

# Add the site-packages path to sys.path for Azure Functions
site_packages_path = os.path.join(os.getcwd(), ".python_packages", "site-packages")
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Testing Azure AD authentication...')
    
    try:
        from shared_code.data import get_connection, HAS_DATABASE
        logging.info(f'HAS_DATABASE = {HAS_DATABASE}')
        
        if HAS_DATABASE:
            logging.info('Attempting to connect to database with Azure AD...')
            try:
                conn = get_connection()
                logging.info('Successfully connected to database with Azure AD!')
                
                # Test a simple query
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM spar.lists")
                result = cursor.fetchone()
                count = result[0] if result else 0
                
                conn.close()
                
                return func.HttpResponse(
                    json.dumps({
                        "message": "Azure AD authentication successful!", 
                        "has_database": HAS_DATABASE,
                        "list_count": count,
                        "authentication_method": "Azure AD"
                    }),
                    mimetype="application/json",
                    status_code=200
                )
            except Exception as db_error:
                logging.error(f"Database connection failed: {db_error}")
                return func.HttpResponse(
                    json.dumps({
                        "message": "Azure AD authentication failed", 
                        "error": str(db_error),
                        "has_database": HAS_DATABASE
                    }),
                    mimetype="application/json",
                    status_code=500
                )
        else:
            logging.warning('HAS_DATABASE is False, Azure AD libraries not available')
            return func.HttpResponse(
                json.dumps({
                    "message": "Azure AD libraries not available", 
                    "has_database": HAS_DATABASE
                }),
                mimetype="application/json",
                status_code=200
            )
            
    except Exception as e:
        logging.error(f"Error testing Azure AD: {e}")
        return func.HttpResponse(
            json.dumps({"message": "Error", "error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
