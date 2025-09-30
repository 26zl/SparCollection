from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

# Import database libraries
import sys
import os

# Add the site-packages path to sys.path for Azure Functions
site_packages_path = os.path.join(os.getcwd(), ".python_packages", "site-packages")
if site_packages_path not in sys.path:
    sys.path.insert(0, site_packages_path)

import psycopg2
import threading
from queue import Queue, Empty
import time

# Global connection pool
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    """Get or create database connection pool"""
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:  # Double-check locking
                try:
                    # Get database connection details from environment variables
                    host = os.getenv("POSTGRES_HOST")
                    database = os.getenv("POSTGRES_DATABASE")
                    user = os.getenv("POSTGRES_USER")
                    password = os.getenv("POSTGRES_PASSWORD")
                    port = os.getenv("POSTGRES_PORT", "5432")
                    
                    # Try to load from local.settings.json for local development
                    if not all([host, database, user, password]):
                        import json
                        try:
                            paths = ['local.settings.json', '../local.settings.json', '/Users/lenti/Local/SparCollection/azure_functions/local.settings.json']
                            for path in paths:
                                try:
                                    with open(path, 'r') as f:
                                        settings = json.load(f)
                                        values = settings.get('Values', {})
                                        host = host or values.get('POSTGRES_HOST')
                                        database = database or values.get('POSTGRES_DATABASE')
                                        user = user or values.get('POSTGRES_USER')
                                        password = password or values.get('POSTGRES_PASSWORD')
                                        port = port or values.get('POSTGRES_PORT', '5432')
                                        if all([host, database, user, password]):
                                            break
                                except:
                                    continue
                        except:
                            pass
                    
                    if not all([host, database, user, password]):
                        raise Exception("Database environment variables are required: POSTGRES_HOST, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD")
                    
                    # Create simple connection pool using Queue
                    _connection_pool = {
                        'queue': Queue(maxsize=10),
                        'host': host,
                        'database': database,
                        'user': user,
                        'password': password,
                        'port': port,
                        'created_connections': 0,
                        'max_connections': 10
                    }
                    
                    # Pre-create one connection
                    conn = psycopg2.connect(
                        host=host,
                        database=database,
                        user=user,
                        password=password,
                        port=port,
                        sslmode='require'
                    )
                    _connection_pool['queue'].put(conn)
                    _connection_pool['created_connections'] = 1
                    
                    logging.info("Created PostgreSQL connection pool")
                    
                except Exception as e:
                    logging.error("Failed to create connection pool: %s", e)
                    raise
    
    return _connection_pool

def get_connection():
    """Get database connection from pool"""
    try:
        pool = get_connection_pool()
        
        # Try to get existing connection
        try:
            conn = pool['queue'].get_nowait()
            return conn
        except Empty:
            pass
        
        # Create new connection if under limit
        with _pool_lock:
            if pool['created_connections'] < pool['max_connections']:
                conn = psycopg2.connect(
                    host=pool['host'],
                    database=pool['database'],
                    user=pool['user'],
                    password=pool['password'],
                    port=pool['port'],
                    sslmode='require'
                )
                pool['created_connections'] += 1
                return conn
        
        # Wait for available connection
        conn = pool['queue'].get(timeout=30)
        return conn
        
    except Exception as e:
        logging.error("Failed to get connection from pool: %s", e)
        raise

def return_connection(conn):
    """Return connection to pool"""
    try:
        pool = get_connection_pool()
        if conn and not conn.closed:
            pool['queue'].put(conn)
    except Exception as e:
        logging.error("Failed to return connection to pool: %s", e)
        if conn:
            try:
                conn.close()
            except:
                pass

def get_lists(shop_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all lists, optionally filtered by shop_id"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if shop_id:
            cursor.execute("""
                SELECT id, shop_id, status, created_at, completed_at, completed_by
                FROM spar.lists 
                WHERE shop_id = %s 
                ORDER BY created_at DESC
            """, (shop_id,))
        else:
            cursor.execute("""
                SELECT id, shop_id, status, created_at, completed_at, completed_by
                FROM spar.lists 
                ORDER BY created_at DESC
            """)
        
        lists = []
        columns = [column[0] for column in cursor.description] if cursor.description else [] if cursor.description else []
        for row in cursor.fetchall():
            row_dict = dict(zip(columns, row))
            list_data = {
                "id": row_dict["id"],
                "shop_id": row_dict["shop_id"],
                "status": row_dict["status"],
                "created_at": row_dict["created_at"].isoformat() + "Z" if row_dict["created_at"] else None,
                "completed_at": row_dict["completed_at"].isoformat() + "Z" if row_dict["completed_at"] else None,
                "completed_by": row_dict["completed_by"],
                "items": []
            }
            
            # Get items for this list
            cursor.execute("""
                SELECT id, sku, name, qty_requested, qty_collected, status, version
                FROM spar.list_items 
                WHERE list_id = %s 
                ORDER BY id
            """, (row_dict["id"],))
            
            item_columns = [column[0] for column in cursor.description] if cursor.description else []
            for item_row in cursor.fetchall():
                item_row_dict = dict(zip(item_columns, item_row))
                item_data = {
                    "id": item_row_dict["id"],
                    "name": item_row_dict["name"],
                    "qty": item_row_dict["qty_requested"],
                    "status": item_row_dict["status"],
                    "version": item_row_dict["version"]
                }
                if item_row_dict["qty_collected"] is not None:
                    item_data["qty_collected"] = item_row_dict["qty_collected"]
                list_data["items"].append(item_data)
            
            lists.append(list_data)
        
        return lists
    except Exception as e:
        logging.error("Error fetching lists: %s", e)
        raise
    finally:
        if conn:
            return_connection(conn)

def get_list(list_id: str, shop_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a specific list by ID"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if shop_id:
            cursor.execute("""
                SELECT id, shop_id, status, created_at, completed_at, completed_by
                FROM spar.lists 
                WHERE id = %s AND shop_id = %s
            """, (list_id, shop_id))
        else:
            cursor.execute("""
                SELECT id, shop_id, status, created_at, completed_at, completed_by
                FROM spar.lists 
                WHERE id = %s
            """, (list_id,))
        
        columns = [column[0] for column in cursor.description] if cursor.description else []
        row = cursor.fetchone()
        if not row:
            return None
        
        row_dict = dict(zip(columns, row))
        list_data = {
            "id": row_dict["id"],
            "shop_id": row_dict["shop_id"],
            "status": row_dict["status"],
            "created_at": row_dict["created_at"].isoformat() + "Z" if row_dict["created_at"] else None,
            "completed_at": row_dict["completed_at"].isoformat() + "Z" if row_dict["completed_at"] else None,
            "completed_by": row_dict["completed_by"],
            "items": []
        }
        
        # Get items for this list
        cursor.execute("""
            SELECT id, sku, name, qty_requested, qty_collected, status, version
            FROM spar.list_items 
            WHERE list_id = %s 
            ORDER BY id
        """, (list_id,))
        
        item_columns = [column[0] for column in cursor.description]
        for item_row in cursor.fetchall():
            item_row_dict = dict(zip(item_columns, item_row))
            item_data = {
                "id": item_row_dict["id"],
                "name": item_row_dict["name"],
                "qty": item_row_dict["qty_requested"],
                "status": item_row_dict["status"],
                "version": item_row_dict["version"]
            }
            if item_row_dict["qty_collected"] is not None:
                item_data["qty_collected"] = item_row_dict["qty_collected"]
            list_data["items"].append(item_data)
        
        return list_data
    except Exception as e:
        logging.error("Error fetching list %s: %s", list_id, e)
        raise
    finally:
        if conn:
            return_connection(conn)

def update_item(list_id: str, item_id: str, status: str, qty_collected: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Update an item in a list"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Update the item
        cursor.execute("""
            UPDATE spar.list_items 
            SET status = %s, qty_collected = COALESCE(%s, qty_collected), version = version + 1
            WHERE list_id = %s AND id = %s
        """, (status, qty_collected, list_id, item_id))
        
        if cursor.rowcount == 0:
            return None
        
        # Get the updated item
        cursor.execute("""
            SELECT id, sku, name, qty_requested, qty_collected, status, version
            FROM spar.list_items 
            WHERE list_id = %s AND id = %s
        """, (list_id, item_id))
        
        columns = [column[0] for column in cursor.description] if cursor.description else []
        row = cursor.fetchone()
        if not row:
            return None
        
        row_dict = dict(zip(columns, row))
        item_data = {
            "id": row_dict["id"],
            "name": row_dict["name"],
            "qty": row_dict["qty_requested"],
            "status": row_dict["status"],
            "version": row_dict["version"]
        }
        if row_dict["qty_collected"] is not None:
            item_data["qty_collected"] = row_dict["qty_collected"]
        
        conn.commit()
        return item_data
    except Exception as e:
        logging.error("Error updating item %s in list %s: %s", item_id, list_id, e)
        raise
    finally:
        if conn:
            return_connection(conn)

def complete_list(list_id: str, completed_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Mark a list as completed"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Update the list status
            cursor.execute("""
                UPDATE spar.lists 
                SET status = 'completed', completed_at = NOW(), completed_by = %s
                WHERE id = %s
            """, (completed_by, list_id))
            
            if cursor.rowcount == 0:
                return None
            
            # Get the updated list
            cursor.execute("""
                SELECT id, shop_id, status, completed_at, completed_by
                FROM spar.lists 
                WHERE id = %s
            """, (list_id,))
            
            columns = [column[0] for column in cursor.description] if cursor.description else []
            row = cursor.fetchone()
            if not row:
                return None
            
            row_dict = dict(zip(columns, row))
            result = {
                "listId": row_dict["id"],
                "status": row_dict["status"],
                "completedAt": row_dict["completed_at"].isoformat() + "Z" if row_dict["completed_at"] else None,
                "completedBy": row_dict["completed_by"]
            }
            
            conn.commit()
            return result
    except Exception as e:
        logging.error("Error completing list %s: %s", list_id, e)
        raise

def create_list(title: str, shop_id: str, items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a new shopping list"""
    import uuid
    from datetime import datetime
    
    list_id = str(uuid.uuid4())[:8]  # Short ID for demo
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Create the list
            cursor.execute("""
                INSERT INTO spar.lists (id, shop_id, status, created_at)
                VALUES (%s, %s, 'active', NOW())
            """, (list_id, shop_id))
            
            # Create items
            if items:
                for item in items:
                    cursor.execute("""
                        INSERT INTO spar.list_items (id, list_id, sku, name, qty_requested, status, version)
                        VALUES (%s, %s, %s, %s, %s, %s, 1)
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
        logging.error("Error creating list: %s", e)
        raise

def delete_list(list_id: str, shop_id: Optional[str] = None) -> bool:
    """Delete a shopping list"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if shop_id:
                cursor.execute("DELETE FROM spar.lists WHERE id = %s AND shop_id = %s", (list_id, shop_id))
            else:
                cursor.execute("DELETE FROM spar.lists WHERE id = %s", (list_id,))
            
            success = cursor.rowcount > 0
            conn.commit()
            return success
    except Exception as e:
        logging.error("Error deleting list %s: %s", list_id, e)
        raise

