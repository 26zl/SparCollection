import json
import logging
import sys
import os

import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Debugging environment...')
    
    debug_info = {
        "python_version": sys.version,
        "python_path": sys.path,
        "working_directory": os.getcwd(),
        "environment_variables": {
            "FUNCTIONS_WORKER_RUNTIME": os.getenv("FUNCTIONS_WORKER_RUNTIME"),
            "PYTHONPATH": os.getenv("PYTHONPATH"),
            "AZURE_SQL_SERVER": os.getenv("AZURE_SQL_SERVER"),
            "AZURE_SQL_DATABASE": os.getenv("AZURE_SQL_DATABASE"),
        }
    }
    
    # Try to list installed packages
    try:
        import pkg_resources
        installed_packages = [d.project_name for d in pkg_resources.working_set]
        debug_info["installed_packages"] = installed_packages
    except Exception as e:
        debug_info["installed_packages_error"] = str(e)
    
    # Check if .python_packages directory exists
    python_packages_path = os.path.join(os.getcwd(), ".python_packages")
    debug_info["python_packages_exists"] = os.path.exists(python_packages_path)
    
    if os.path.exists(python_packages_path):
        try:
            contents = os.listdir(python_packages_path)
            debug_info["python_packages_contents"] = contents
        except Exception as e:
            debug_info["python_packages_list_error"] = str(e)
    
    return func.HttpResponse(
        json.dumps(debug_info, indent=2),
        mimetype="application/json",
        status_code=200
    )
