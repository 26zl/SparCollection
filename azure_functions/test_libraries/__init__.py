import json
import logging

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Testing available libraries...')
    
    libraries = {}
    
    # Test pyodbc
    try:
        import pyodbc
        libraries['pyodbc'] = 'available'
        logging.info('pyodbc is available')
    except ImportError as e:
        libraries['pyodbc'] = f'not available: {e}'
        logging.warning('pyodbc not available: %s', e)
    
    # Test azure-identity
    try:
        from azure.identity import DefaultAzureCredential
        libraries['azure-identity'] = 'available'
        logging.info('azure-identity is available')
    except ImportError as e:
        libraries['azure-identity'] = f'not available: {e}'
        logging.warning('azure-identity not available: %s', e)
    
    # Test pymssql
    try:
        import pymssql
        libraries['pymssql'] = 'available'
        logging.info('pymssql is available')
    except ImportError as e:
        libraries['pymssql'] = f'not available: {e}'
        logging.warning('pymssql not available: %s', e)
    
    # Test azure-servicebus
    try:
        import azure.servicebus
        libraries['azure-servicebus'] = 'available'
        logging.info('azure-servicebus is available')
    except ImportError as e:
        libraries['azure-servicebus'] = f'not available: {e}'
        logging.warning('azure-servicebus not available: %s', e)
    
    return func.HttpResponse(
        json.dumps({
            "message": "Library availability test",
            "libraries": libraries
        }),
        mimetype="application/json",
        status_code=200
    )
