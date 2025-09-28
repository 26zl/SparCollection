from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Hardcode data path for Azure Functions - it should be in the root of the function app
DATA_ROOT = Path("data")


def load_json(name: str) -> Any:
    path = DATA_ROOT / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def persist_json(name: str, payload: Any) -> None:
    import logging
    
    path = DATA_ROOT / name
    logging.info("Attempting to save to path: %s", str(path.absolute()))
    logging.info("Current working directory: %s", os.getcwd())
    logging.info("DATA_ROOT exists: %s", DATA_ROOT.exists())
    
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
        logging.info("Successfully saved to %s", str(path))
    except Exception as e:
        logging.error("Failed to save to %s: %s", str(path), str(e))
        raise
