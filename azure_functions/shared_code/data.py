from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Hardcode data path for Azure Functions - it should be in the root of the function app
DATA_ROOT = Path("data")

# In-memory storage as fallback
_memory_storage = {
    "lists.json": [
        {
            "id": "abc123",
            "title": "Liste abc123", 
            "status": "active",
            "shop_id": "NO-TR-001",
            "items": [
                {
                    "id": "item-100",
                    "name": "Melk 1L",
                    "qty": 2,
                    "status": "pending",
                    "version": 1
                },
                {
                    "id": "item-101",
                    "name": "Brød grovt",
                    "qty": 1,
                    "status": "pending",
                    "version": 1
                },
                {
                    "id": "item-102",
                    "name": "Epler",
                    "qty": 6,
                    "status": "pending",
                    "version": 1
                }
            ]
        }
    ],
    "employees.json": [],
    "stock.json": []
}


def load_json(name: str) -> Any:
    import logging
    
    # Try to load from file first
    path = DATA_ROOT / name
    logging.info("Attempting to load from path: %s", str(path.absolute()))
    logging.info("Current working directory: %s", os.getcwd())
    logging.info("DATA_ROOT exists: %s", DATA_ROOT.exists())
    logging.info("File exists: %s", path.exists())
    
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            logging.info("Successfully loaded data from %s", str(path))
            return data
    except Exception as e:
        logging.warning("Failed to load from %s: %s, using in-memory fallback", str(path), str(e))
        # Fallback to in-memory storage
        if name in _memory_storage:
            logging.info("Using in-memory data for %s", name)
            return _memory_storage[name]
        else:
            logging.error("No in-memory data available for %s", name)
            raise


def persist_json(name: str, payload: Any) -> None:
    import logging
    
    # Update in-memory storage first
    if name in _memory_storage:
        _memory_storage[name] = payload
        logging.info("Updated in-memory storage for %s", name)
    
    # Try to save to file
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
        logging.warning("Failed to save to %s: %s, but in-memory storage updated", str(path), str(e))
        # Don't raise exception - in-memory storage was updated
