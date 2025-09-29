import json
import logging
import os

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Listing packages in site-packages...')
    
    python_packages_path = os.path.join(os.getcwd(), ".python_packages", "site-packages")
    
    packages_info = {
        "path": python_packages_path,
        "exists": os.path.exists(python_packages_path),
        "contents": []
    }
    
    if os.path.exists(python_packages_path):
        try:
            contents = os.listdir(python_packages_path)
            packages_info["contents"] = contents
            
            # Look for specific packages we need
            target_packages = ["pyodbc", "azure", "pymssql"]
            found_packages = {}
            
            for package in target_packages:
                found_packages[package] = any(package in item for item in contents)
            
            packages_info["target_packages_found"] = found_packages
            
        except Exception as e:
            packages_info["error"] = str(e)
    
    return func.HttpResponse(
        json.dumps(packages_info, indent=2),
        mimetype="application/json",
        status_code=200
    )
