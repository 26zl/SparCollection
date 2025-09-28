from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Use a simple in-memory storage for now
_data = {
    "lists": [
        {
            "id": "abc123",
            "title": "Liste abc123",
            "status": "active",
            "shop_id": "NO-TR-001",
            "items": [
                {"id": "item-100", "name": "Melk 1L", "qty": 2, "status": "pending", "version": 1},
                {"id": "item-101", "name": "Brød grovt", "qty": 1, "status": "pending", "version": 1},
                {"id": "item-102", "name": "Epler", "qty": 6, "status": "pending", "version": 1}
            ]
        }
    ]
}

def get_lists(shop_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all lists, optionally filtered by shop_id"""
    lists = _data["lists"]
    if shop_id:
        lists = [l for l in lists if l.get("shop_id") == shop_id or l.get("shop_id") is None]
    return lists

def get_list(list_id: str, shop_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a specific list by ID"""
    for list_item in _data["lists"]:
        if list_item["id"] == list_id:
            if shop_id and list_item.get("shop_id") != shop_id and list_item.get("shop_id") is not None:
                continue
            return list_item
    return None

def update_item(list_id: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an item in a list"""
    for list_item in _data["lists"]:
        if list_item["id"] == list_id:
            for item in list_item["items"]:
                if item["id"] == item_id:
                    # Update allowed fields
                    if "status" in updates:
                        item["status"] = updates["status"]
                    if "qty" in updates:
                        item["qty"] = updates["qty"]
                    item["version"] += 1
                    return item
    return None

def complete_list(list_id: str, completed_by: Optional[str] = None) -> bool:
    """Mark a list as completed"""
    for list_item in _data["lists"]:
        if list_item["id"] == list_id:
            list_item["status"] = "completed"
            return True
    return False

def init_database():
    """Initialize database - no-op for JSON storage"""
    pass

def create_sample_data():
    """Create sample data - already exists in _data"""
    pass
