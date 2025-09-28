from __future__ import annotations

import json
import logging
import os
import pyodbc
from typing import Any, Dict, List, Optional

# Database connection string from environment
CONNECTION_STRING = os.environ.get("SQL_CONNECTION_STRING", "")

def get_connection():
    """Get database connection"""
    if not CONNECTION_STRING:
        raise Exception("SQL_CONNECTION_STRING environment variable not set")
    
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except Exception as e:
        logging.error("Failed to connect to database: %s", str(e))
        raise

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create lists table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='lists' AND xtype='U')
            CREATE TABLE lists (
                id NVARCHAR(50) PRIMARY KEY,
                title NVARCHAR(255) NOT NULL,
                status NVARCHAR(50) NOT NULL,
                shop_id NVARCHAR(50),
                created_at DATETIME2 DEFAULT GETUTCDATE(),
                updated_at DATETIME2 DEFAULT GETUTCDATE()
            )
        """)
        
        # Create items table
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='items' AND xtype='U')
            CREATE TABLE items (
                id NVARCHAR(50) PRIMARY KEY,
                list_id NVARCHAR(50) NOT NULL,
                name NVARCHAR(255) NOT NULL,
                qty INT NOT NULL DEFAULT 1,
                status NVARCHAR(50) NOT NULL DEFAULT 'pending',
                version INT NOT NULL DEFAULT 1,
                created_at DATETIME2 DEFAULT GETUTCDATE(),
                updated_at DATETIME2 DEFAULT GETUTCDATE(),
                FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        logging.info("Database tables initialized successfully")
        
    except Exception as e:
        logging.error("Failed to initialize database: %s", str(e))
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_lists(shop_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all lists, optionally filtered by shop_id"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if shop_id:
            cursor.execute("""
                SELECT l.id, l.title, l.status, l.shop_id, l.created_at, l.updated_at
                FROM lists l
                WHERE l.shop_id = ? OR l.shop_id IS NULL
                ORDER BY l.created_at DESC
            """, (shop_id,))
        else:
            cursor.execute("""
                SELECT l.id, l.title, l.status, l.shop_id, l.created_at, l.updated_at
                FROM lists l
                ORDER BY l.created_at DESC
            """)
        
        rows = cursor.fetchall()
        lists = []
        
        for row in rows:
            list_data = {
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "shop_id": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "updated_at": row[5].isoformat() if row[5] else None,
                "items": []
            }
            
            # Get items for this list
            cursor.execute("""
                SELECT id, name, qty, status, version
                FROM items
                WHERE list_id = ?
                ORDER BY created_at
            """, (row[0],))
            
            item_rows = cursor.fetchall()
            for item_row in item_rows:
                list_data["items"].append({
                    "id": item_row[0],
                    "name": item_row[1],
                    "qty": item_row[2],
                    "status": item_row[3],
                    "version": item_row[4]
                })
            
            lists.append(list_data)
        
        return lists
        
    except Exception as e:
        logging.error("Failed to get lists: %s", str(e))
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_list(list_id: str, shop_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Get a specific list by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if shop_id:
            cursor.execute("""
                SELECT l.id, l.title, l.status, l.shop_id, l.created_at, l.updated_at
                FROM lists l
                WHERE l.id = ? AND (l.shop_id = ? OR l.shop_id IS NULL)
            """, (list_id, shop_id))
        else:
            cursor.execute("""
                SELECT l.id, l.title, l.status, l.shop_id, l.created_at, l.updated_at
                FROM lists l
                WHERE l.id = ?
            """, (list_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        list_data = {
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "shop_id": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "updated_at": row[5].isoformat() if row[5] else None,
            "items": []
        }
        
        # Get items for this list
        cursor.execute("""
            SELECT id, name, qty, status, version
            FROM items
            WHERE list_id = ?
            ORDER BY created_at
        """, (list_id,))
        
        item_rows = cursor.fetchall()
        for item_row in item_rows:
            list_data["items"].append({
                "id": item_row[0],
                "name": item_row[1],
                "qty": item_row[2],
                "status": item_row[3],
                "version": item_row[4]
            })
        
        return list_data
        
    except Exception as e:
        logging.error("Failed to get list %s: %s", list_id, str(e))
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def update_item(list_id: str, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an item in a list"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if list exists
        cursor.execute("SELECT id FROM lists WHERE id = ?", (list_id,))
        if not cursor.fetchone():
            return None
        
        # Check if item exists
        cursor.execute("SELECT id FROM items WHERE id = ? AND list_id = ?", (item_id, list_id))
        if not cursor.fetchone():
            return None
        
        # Build update query
        set_clauses = []
        params = []
        
        for key, value in updates.items():
            if key in ['status', 'qty']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if not set_clauses:
            return None
        
        # Add version increment
        set_clauses.append("version = version + 1")
        set_clauses.append("updated_at = GETUTCDATE()")
        
        params.extend([item_id, list_id])
        
        cursor.execute(f"""
            UPDATE items 
            SET {', '.join(set_clauses)}
            WHERE id = ? AND list_id = ?
        """, params)
        
        # Get updated item
        cursor.execute("""
            SELECT id, name, qty, status, version
            FROM items
            WHERE id = ? AND list_id = ?
        """, (item_id, list_id))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        conn.commit()
        
        return {
            "id": row[0],
            "name": row[1],
            "qty": row[2],
            "status": row[3],
            "version": row[4]
        }
        
    except Exception as e:
        logging.error("Failed to update item %s in list %s: %s", item_id, list_id, str(e))
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def complete_list(list_id: str, completed_by: Optional[str] = None) -> bool:
    """Mark a list as completed"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE lists 
            SET status = 'completed', updated_at = GETUTCDATE()
            WHERE id = ?
        """, (list_id,))
        
        if cursor.rowcount == 0:
            return False
        
        conn.commit()
        return True
        
    except Exception as e:
        logging.error("Failed to complete list %s: %s", list_id, str(e))
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def create_sample_data():
    """Create sample data for testing"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM lists")
        if cursor.fetchone()[0] > 0:
            logging.info("Sample data already exists")
            return
        
        # Insert sample list
        cursor.execute("""
            INSERT INTO lists (id, title, status, shop_id)
            VALUES (?, ?, ?, ?)
        """, ("abc123", "Liste abc123", "active", "NO-TR-001"))
        
        # Insert sample items
        sample_items = [
            ("item-100", "abc123", "Melk 1L", 2, "pending", 1),
            ("item-101", "abc123", "Brød grovt", 1, "pending", 1),
            ("item-102", "abc123", "Epler", 6, "pending", 1)
        ]
        
        for item in sample_items:
            cursor.execute("""
                INSERT INTO items (id, list_id, name, qty, status, version)
                VALUES (?, ?, ?, ?, ?, ?)
            """, item)
        
        conn.commit()
        logging.info("Sample data created successfully")
        
    except Exception as e:
        logging.error("Failed to create sample data: %s", str(e))
        raise
    finally:
        if 'conn' in locals():
            conn.close()
