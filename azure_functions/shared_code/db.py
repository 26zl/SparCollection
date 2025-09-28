from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Generator, List, Optional

import pyodbc


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        # Preserve integers without decimal point when possible
        return int(value) if value == int(value) else float(value)
    return value


def _row_to_dict(cursor: pyodbc.Cursor, row: Any) -> Dict[str, Any]:
    columns = [col[0] for col in cursor.description]
    return {column: _serialize_value(value) for column, value in zip(columns, row)}


@contextmanager
def get_conn() -> Generator[pyodbc.Connection, None, None]:
    conn_str = os.getenv("SQL_CONNECTION_STRING")
    if not conn_str:
        logging.error("SQL_CONNECTION_STRING environment variable is not set")
        raise RuntimeError("SQL connection is not configured")

    full_conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        f"{conn_str.rstrip(';')};"
        "Encrypt=yes;TrustServerCertificate=no;"
    )

    conn: Optional[pyodbc.Connection] = None
    try:
        conn = pyodbc.connect(full_conn_str, autocommit=False)
        yield conn
    except pyodbc.Error:
        logging.exception("Failed to connect to SQL database")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                logging.warning("Failed to close SQL connection", exc_info=True)


def fetch_lists(shop_id: str) -> List[Dict[str, Any]]:
    query = (
        "SELECT id, shop_id, status, created_at, completed_at, completed_by "
        "FROM spar.lists WHERE shop_id = ? ORDER BY created_at DESC"
    )

    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (shop_id,))
                rows = cursor.fetchall()
                return [_row_to_dict(cursor, row) for row in rows]
    except pyodbc.Error:
        logging.exception("Error fetching lists for shop %s", shop_id)
        raise


def fetch_list_with_items(list_id: str, shop_id: Optional[str]) -> Optional[Dict[str, Any]]:
    list_query = (
        "SELECT id, shop_id, status, created_at, completed_at, completed_by "
        "FROM spar.lists WHERE id = ?"
    )
    params: List[Any] = [list_id]
    if shop_id:
        list_query += " AND shop_id = ?"
        params.append(shop_id)

    items_query = (
        "SELECT id, list_id, sku, name, qty_requested, qty_collected, status, version "
        "FROM spar.list_items WHERE list_id = ? ORDER BY id"
    )

    try:
        with get_conn() as conn:
            with conn.cursor() as cursor:
                cursor.execute(list_query, tuple(params))
                row = cursor.fetchone()
                if not row:
                    return None
                list_columns = [col[0] for col in cursor.description]
                list_data = {column: _serialize_value(value) for column, value in zip(list_columns, row)}

            with conn.cursor() as cursor:
                cursor.execute(items_query, (list_id,))
                items_rows = cursor.fetchall()
                items = [_row_to_dict(cursor, item_row) for item_row in items_rows]

        list_data["items"] = items
        return list_data
    except pyodbc.Error:
        logging.exception("Error fetching list %s (shop %s)", list_id, shop_id)
        raise


def update_item(
    list_id: str,
    item_id: str,
    status: str,
    qty_collected: Optional[int],
) -> Optional[Dict[str, Any]]:
    update_query = (
        "UPDATE spar.list_items SET status = ?, qty_collected = COALESCE(?, qty_collected), "
        "version = version + 1 WHERE list_id = ? AND id = ?"
    )
    select_query = (
        "SELECT id, list_id, sku, name, qty_requested, qty_collected, status, version "
        "FROM spar.list_items WHERE list_id = ? AND id = ?"
    )

    try:
        with get_conn() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(update_query, status, qty_collected, list_id, item_id)
                    if cursor.rowcount == 0:
                        conn.rollback()
                        return None

                with conn.cursor() as cursor:
                    cursor.execute(select_query, list_id, item_id)
                    row = cursor.fetchone()
                    if not row:
                        conn.rollback()
                        return None
                    item = _row_to_dict(cursor, row)

                conn.commit()
                return item
            except pyodbc.Error:
                conn.rollback()
                logging.exception(
                    "Error updating item %s in list %s", item_id, list_id
                )
                raise
    except pyodbc.Error:
        raise


def complete_list(list_id: str, employee_id: Optional[str]) -> Optional[Dict[str, Any]]:
    update_query = (
        "UPDATE spar.lists SET status = 'COMPLETED', completed_at = SYSUTCDATETIME(), "
        "completed_by = ? WHERE id = ?"
    )
    select_query = (
        "SELECT id, shop_id, status, completed_at, completed_by FROM spar.lists WHERE id = ?"
    )

    try:
        with get_conn() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(update_query, employee_id, list_id)
                    if cursor.rowcount == 0:
                        conn.rollback()
                        return None

                with conn.cursor() as cursor:
                    cursor.execute(select_query, list_id)
                    row = cursor.fetchone()
                    if not row:
                        conn.rollback()
                        return None
                    result = _row_to_dict(cursor, row)

                conn.commit()
            except pyodbc.Error:
                conn.rollback()
                logging.exception("Error completing list %s", list_id)
                raise
    except pyodbc.Error:
        raise

    return {
        "listId": result.get("id"),
        "status": result.get("status"),
        "completedAt": result.get("completed_at"),
        "completedBy": result.get("completed_by"),
    }
