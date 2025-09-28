from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

# Try to import pyodbc and azure.identity, fallback to in-memory if not available
try:
    import pyodbc
    import struct
    from azure import identity
    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    logging.warning("pyodbc or azure.identity not available, using in-memory fallback")

def get_connection():
    """Get database connection using Azure Identity"""
    try:
        # Get connection string from environment
        conn_str = os.getenv("SQL_CONNECTION_STRING")
        if not conn_str:
            # Try to load from local.settings.json for local development
            import json
            try:
                paths = ['local.settings.json', '../local.settings.json', '/Users/lenti/Local/SparCollection/azure_functions/local.settings.json']
                for path in paths:
                    try:
                        with open(path, 'r') as f:
                            settings = json.load(f)
                            conn_str = settings.get('Values', {}).get('SQL_CONNECTION_STRING')
                            if conn_str:
                                break
                    except:
                        continue
            except:
                pass
        
        if not conn_str:
            raise Exception("SQL_CONNECTION_STRING environment variable is required")
        
        # Try different connection approaches
        # Use Azure Identity for authentication
        credential = identity.DefaultAzureCredential(exclude_interactive_browser_credential=False)
        token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
        token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        
        try:
            # Approach 1: Try with ODBC Driver 18
            conn_str_18 = conn_str.replace('Server=tcp:', 'DRIVER={ODBC Driver 18 for SQL Server};SERVER=tcp:')
            conn_str_18 = conn_str_18.replace('User Id=', 'UID=')
            conn_str_18 = conn_str_18.replace('Password=', 'PWD=')
            conn_str_18 = conn_str_18.replace('Encrypt=True', 'Encrypt=yes')
            conn_str_18 = conn_str_18.replace('TrustServerCertificate=False', 'TrustServerCertificate=no')
            
            conn = pyodbc.connect(conn_str_18, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
            return conn
        except Exception as e1:
            logging.warning("ODBC Driver 18 failed: %s", str(e1))
            
            try:
                # Approach 2: Try with ODBC Driver 17
                conn_str_17 = conn_str.replace('Server=tcp:', 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=tcp:')
                conn_str_17 = conn_str_17.replace('User Id=', 'UID=')
                conn_str_17 = conn_str_17.replace('Password=', 'PWD=')
                conn_str_17 = conn_str_17.replace('Encrypt=True', 'Encrypt=yes')
                conn_str_17 = conn_str_17.replace('TrustServerCertificate=False', 'TrustServerCertificate=no')
                
                conn = pyodbc.connect(conn_str_17, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
                return conn
            except Exception as e2:
                logging.warning("ODBC Driver 17 failed: %s", str(e2))
                
                try:
                    # Approach 3: Try with SQL Server driver
                    conn_str_sql = conn_str.replace('Server=tcp:', 'DRIVER={SQL Server};SERVER=tcp:')
                    conn_str_sql = conn_str_sql.replace('User Id=', 'UID=')
                    conn_str_sql = conn_str_sql.replace('Password=', 'PWD=')
                    conn_str_sql = conn_str_sql.replace('Encrypt=True', 'Encrypt=yes')
                    conn_str_sql = conn_str_sql.replace('TrustServerCertificate=False', 'TrustServerCertificate=no')
                    
                    conn = pyodbc.connect(conn_str_sql, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})
                    return conn
                except Exception as e3:
                    logging.error("All ODBC drivers failed: %s, %s, %s", str(e1), str(e2), str(e3))
                    raise Exception("No compatible ODBC driver found")
        
    except Exception as e:
        logging.error("Failed to connect to database: ?", e)
        raise

def get_lists(shop_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all lists, optionally filtered by shop_id"""
    if not HAS_DATABASE:
        return _get_lists_fallback(shop_id)
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if shop_id:
                    cursor.execute("""
                        SELECT id, shop_id, status, created_at, completed_at, completed_by
                        FROM spar.lists 
                        WHERE shop_id = ? 
                        ORDER BY created_at DESC
                    """, (shop_id,))
                else:
                    cursor.execute("""
                        SELECT id, shop_id, status, created_at, completed_at, completed_by
                        FROM spar.lists 
                        ORDER BY created_at DESC
                    """)
                
                lists = []
                for row in cursor.fetchall():
                    list_data = {
                        "id": row[0],
                        "shop_id": row[1],
                        "status": row[2],
                        "created_at": row[3].isoformat() + "Z" if row[3] else None,
                        "completed_at": row[4].isoformat() + "Z" if row[4] else None,
                        "completed_by": row[5],
                        "items": []
                    }
                    
                    # Get items for this list
                    cursor.execute("""
                        SELECT id, sku, name, qty_requested, qty_collected, status, version
                        FROM spar.list_items 
                        WHERE list_id = ? 
                        ORDER BY id
                    """, (row[0],))
                    
                    for item_row in cursor.fetchall():
                        item_data = {
                            "id": item_row[0],
                            "name": item_row[2],
                            "qty": item_row[3],
                            "status": item_row[5],
                            "version": item_row[6]
                        }
                        if item_row[4] is not None:
                            item_data["qty_collected"] = item_row[4]
                        list_data["items"].append(item_data)
                    
                    lists.append(list_data)
                
                return lists
    except Exception as e:
        logging.error("Error fetching lists: ?", e)
        raise

def get_list(list_id: str, shop_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a specific list by ID"""
    if not HAS_DATABASE:
        return _get_list_fallback(list_id, shop_id or "NO-TR-001")
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if shop_id:
                    cursor.execute("""
                        SELECT id, shop_id, status, created_at, completed_at, completed_by
                        FROM spar.lists 
                        WHERE id = ? AND shop_id = ?
                    """, (list_id, shop_id))
                else:
                    cursor.execute("""
                        SELECT id, shop_id, status, created_at, completed_at, completed_by
                        FROM spar.lists 
                        WHERE id = ?
                    """, (list_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                list_data = {
                    "id": row["id"],
                    "shop_id": row["shop_id"],
                    "status": row["status"],
                    "created_at": row["created_at"].isoformat() + "Z" if row["created_at"] else None,
                    "completed_at": row["completed_at"].isoformat() + "Z" if row["completed_at"] else None,
                    "completed_by": row["completed_by"],
                    "items": []
                }
                
                # Get items for this list
                cursor.execute("""
                    SELECT id, sku, name, qty_requested, qty_collected, status, version
                    FROM spar.list_items 
                    WHERE list_id = ? 
                    ORDER BY id
                """, (list_id,))
                
                for item_row in cursor.fetchall():
                    item_data = {
                        "id": item_row["id"],
                        "name": item_row["name"],
                        "qty": item_row["qty_requested"],
                        "status": item_row["status"],
                        "version": item_row["version"]
                    }
                    if item_row["qty_collected"] is not None:
                        item_data["qty_collected"] = item_row["qty_collected"]
                    list_data["items"].append(item_data)
                
                return list_data
    except Exception as e:
        logging.error("Error fetching list ?: ?", list_id, e)
        raise

def update_item(list_id: str, item_id: str, status: str, qty_collected: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Update an item in a list"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Update the item
                cursor.execute("""
                    UPDATE spar.list_items 
                    SET status = ?, qty_collected = COALESCE(?, qty_collected), version = version + 1
                    WHERE list_id = ? AND id = ?
                """, (status, qty_collected, list_id, item_id))
                
                if cursor.rowcount == 0:
                    return None
                
                # Get the updated item
                cursor.execute("""
                    SELECT id, sku, name, qty_requested, qty_collected, status, version
                    FROM spar.list_items 
                    WHERE list_id = ? AND id = ?
                """, (list_id, item_id))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                item_data = {
                    "id": row[0],
                    "name": row[2],
                    "qty": row[3],
                    "status": row[5],
                    "version": row[6]
                }
                if row[4] is not None:
                    item_data["qty_collected"] = row[4]
                
                conn.commit()
                return item_data
    except Exception as e:
        logging.error("Error updating item ? in list ?: ?", item_id, list_id, e)
        raise

def complete_list(list_id: str, completed_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Mark a list as completed"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Update the list status
                cursor.execute("""
                    UPDATE spar.lists 
                    SET status = 'completed', completed_at = SYSUTCDATETIME(), completed_by = ?
                    WHERE id = ?
                """, (completed_by, list_id))
                
                if cursor.rowcount == 0:
                    return None
                
                # Get the updated list
                cursor.execute("""
                    SELECT id, shop_id, status, completed_at, completed_by
                    FROM spar.lists 
                    WHERE id = ?
                """, (list_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                result = {
                    "listId": row[0],
                    "status": row[2],
                    "completedAt": row[3].isoformat() + "Z" if row[3] else None,
                    "completedBy": row[4]
                }
                
                conn.commit()
                return result
    except Exception as e:
        logging.error("Error completing list ?: ?", list_id, e)
        raise

def create_list(title: str, shop_id: str, items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new shopping list"""
    import uuid
    from datetime import datetime
    
    list_id = str(uuid.uuid4())[:8]  # Short ID for demo
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Create the list
                cursor.execute("""
                    INSERT INTO spar.lists (id, shop_id, status, created_at)
                    VALUES (?, ?, 'active', SYSUTCDATETIME())
                """, (list_id, shop_id))
                
                # Create items
                if items:
                    for item in items:
                        cursor.execute("""
                            INSERT INTO spar.list_items (id, list_id, sku, name, qty_requested, status, version)
                            VALUES (?, ?, ?, ?, ?, ?, 1)
                        """, (
                            item.get("id", str(uuid.uuid4())[:12]),
                            list_id,
                            item.get("sku"),
                            item["name"],
                            item["qty"],
                            item.get("status", "pending")
                        ))
                
                conn.commit()
                
                # Return the created list
                return get_list(list_id, shop_id) or {
                    "id": list_id,
                    "title": title,
                    "status": "active",
                    "shop_id": shop_id,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "items": items or []
                }
    except Exception as e:
        logging.error("Error creating list: ?", e)
        raise

def delete_list(list_id: str, shop_id: Optional[str] = None) -> bool:
    """Delete a shopping list"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                if shop_id:
                    cursor.execute("DELETE FROM spar.lists WHERE id = ? AND shop_id = ?", (list_id, shop_id))
                else:
                    cursor.execute("DELETE FROM spar.lists WHERE id = ?", (list_id,))
                
                success = cursor.rowcount > 0
                conn.commit()
                return success
    except Exception as e:
        logging.error("Error deleting list ?: ?", list_id, e)
        raise

# Fallback functions for when database is not available
def _get_lists_fallback(shop_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fallback to in-memory data when database is not available"""
    # Sample data for fallback
    sample_lists = [
        {
            "id": "abc123",
            "shop_id": "NO-TR-001",
            "status": "completed",
            "created_at": "2025-09-28T21:19:57.532766Z",
            "completed_at": "2025-09-28T21:52:11.224031Z",
            "completed_by": "test",
            "items": [
                {"id": "item-100", "name": "Melk 1L", "qty": 2, "qtyCollected": 0, "status": "unavailable", "version": 4},
                {"id": "item-101", "name": "Brød grovt", "qty": 1, "qtyCollected": 0, "status": "unavailable", "version": 2},
                {"id": "item-102", "name": "Epler", "qty": 6, "qtyCollected": 0, "status": "unavailable", "version": 3}
            ]
        },
        {
            "id": "def456",
            "shop_id": "NO-TR-001",
            "status": "completed",
            "created_at": "2025-09-28T21:19:57.564018Z",
            "completed_at": "2025-09-28T21:52:49.009874Z",
            "completed_by": "emp_def456",
            "items": [
                {"id": "item-200", "name": "Kaffekopp", "qty": 4, "qtyCollected": 0, "status": "pending", "version": 1},
                {"id": "item-201", "name": "Tallerken", "qty": 6, "qtyCollected": 0, "status": "pending", "version": 1}
            ]
        }
    ]
    
    if shop_id:
        return [list_item for list_item in sample_lists if list_item["shop_id"] == shop_id]
    return sample_lists

def _get_list_fallback(list_id: str, shop_id: str) -> Optional[Dict[str, Any]]:
    """Fallback to in-memory data when database is not available"""
    lists = _get_lists_fallback(shop_id)
    for list_item in lists:
        if list_item["id"] == list_id:
            return list_item
    return None

def init_database():
    """Initialize database - no-op for database storage"""
    pass

def create_sample_data():
    """Create sample data - no-op for database storage"""
    pass