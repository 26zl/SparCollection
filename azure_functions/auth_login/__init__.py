import json
import logging
from datetime import datetime
import bcrypt

import azure.functions as func

from shared_code.data import get_connection, return_connection


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Authenticate user and return user data
    POST /api/auth_login
    Body: { "username": "...", "password": "..." }
    """

    try:
        body = json.loads(req.get_body())
    except ValueError:
        return func.HttpResponse(
            body=json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return func.HttpResponse(
            body=json.dumps({"error": "Username and password required"}),
            status_code=400,
            mimetype="application/json"
        )

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get user from database
        cursor.execute("""
            SELECT id, username, password_hash, shop_id, role, active
            FROM spar.users
            WHERE username = %s
        """, (username,))

        row = cursor.fetchone()

        if not row:
            logging.warning(f"Login attempt for non-existent user: {username}")
            return func.HttpResponse(
                body=json.dumps({"error": "Invalid credentials"}),
                status_code=401,
                mimetype="application/json"
            )

        user_id, db_username, password_hash, shop_id, role, active = row

        if not active:
            logging.warning(f"Login attempt for inactive user: {username}")
            return func.HttpResponse(
                body=json.dumps({"error": "Account disabled"}),
                status_code=401,
                mimetype="application/json"
            )

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            logging.warning(f"Failed login attempt for user: {username}")
            return func.HttpResponse(
                body=json.dumps({"error": "Invalid credentials"}),
                status_code=401,
                mimetype="application/json"
            )

        # Update last login
        cursor.execute("""
            UPDATE spar.users
            SET last_login = NOW()
            WHERE id = %s
        """, (user_id,))
        conn.commit()

        logging.info(f"Successful login: {username} ({shop_id})")

        # Return user data (no password)
        return func.HttpResponse(
            body=json.dumps({
                "id": user_id,
                "username": db_username,
                "shopId": shop_id,
                "role": role
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Error during login")
        return func.HttpResponse(
            body=json.dumps({"error": "Server error"}),
            status_code=500,
            mimetype="application/json"
        )
    finally:
        if conn:
            return_connection(conn)
