import json
import logging
import sys
import os

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Testing direct imports...')
    
    results = {}
    
    # Add the site-packages path to sys.path
    site_packages_path = os.path.join(os.getcwd(), ".python_packages", "site-packages")
    if site_packages_path not in sys.path:
        sys.path.insert(0, site_packages_path)
        logging.info(f"Added {site_packages_path} to sys.path")
    
    # Test pyodbc
    try:
        import pyodbc
        results['pyodbc'] = 'success'
        results['pyodbc_version'] = getattr(pyodbc, '__version__', 'unknown')
        logging.info('pyodbc imported successfully')
    except Exception as e:
        results['pyodbc'] = f'failed: {e}'
        logging.error('pyodbc import failed: %s', e)
    
    # Test azure-identity
    try:
        from azure.identity import DefaultAzureCredential
        results['azure-identity'] = 'success'
        logging.info('azure-identity imported successfully')
    except Exception as e:
        results['azure-identity'] = f'failed: {e}'
        logging.error('azure-identity import failed: %s', e)
    
    # Test azure-servicebus
    try:
        import azure.servicebus
        results['azure-servicebus'] = 'success'
        logging.info('azure-servicebus imported successfully')
    except Exception as e:
        results['azure-servicebus'] = f'failed: {e}'
        logging.error('azure-servicebus import failed: %s', e)
    
    return func.HttpResponse(
        json.dumps({
            "message": "Direct import test",
            "results": results,
            "sys_path": sys.path[:5]  # First 5 entries
        }),
        mimetype="application/json",
        status_code=200
    )
