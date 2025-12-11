import json
import logging
from datetime import datetime
from typing import Any, Dict

import azure.functions as func


def main(msg: func.ServiceBusMessage) -> None:
    """Process completed shopping lists for payment"""
    
    try:
        # Parse the message
        message_body = msg.get_body().decode('utf-8')
        payment_data = json.loads(message_body)
        
        logging.info("Processing payment for list: %s", payment_data.get("listId"))
        
        # Simulate payment processing
        result = process_payment(payment_data)
        
        if result["success"]:
            logging.info("Payment processed successfully for list %s: %s", 
                       payment_data.get("listId"), result["transactionId"])
        else:
            logging.error("Payment failed for list %s: %s", 
                         payment_data.get("listId"), result["error"])
            
    except Exception as e:
        logging.exception("Error processing payment message: %s", e)


def process_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process payment for a completed shopping list"""

    list_id = payment_data.get("listId")
    shop_id = payment_data.get("shopId")
    completed_by = payment_data.get("completedBy")
    completed_at = payment_data.get("completedAt")
    items = payment_data.get("items", [])
    title = payment_data.get("title", "Unknown List")

    # Validate required payment data
    if not all([list_id, shop_id, completed_by]):
        missing = []
        if not list_id: missing.append("listId")
        if not shop_id: missing.append("shopId")
        if not completed_by: missing.append("completedBy")

        return {
            "success": False,
            "error": f"Missing required payment data: {', '.join(missing)}",
            "transactionId": None
        }

    # Calculate total amount from database pricing
    total_amount = calculate_total_amount(items)

    try:
        # Generate transaction ID
        transaction_id = f"TXN-{list_id}-{int(datetime.now().timestamp())}"

        # Log payment details
        logging.info("Payment processed: List=%s (%s), Shop=%s, Items=%d, Amount=%.2f, Transaction=%s",
                   list_id, title, shop_id, len(items), total_amount, transaction_id)

        return {
            "success": True,
            "transactionId": transaction_id,
            "amount": total_amount,
            "processedAt": datetime.utcnow().isoformat() + "Z",
            "listId": list_id,
            "shopId": shop_id,
            "completedBy": completed_by
        }
    except Exception as e:
        logging.error("Payment processing failed for list %s: %s", list_id, e)
        return {
            "success": False,
            "error": f"Payment processing error: {str(e)}",
            "transactionId": None
        }


def calculate_total_amount(items: list) -> float:
    """Calculate total amount for the shopping list based on actual item prices from database"""

    if not items:
        return 0.0

    try:
        # Import database functions
        import sys
        import os
        site_packages_path = os.path.join(os.getcwd(), ".python_packages", "site-packages")
        if site_packages_path not in sys.path:
            sys.path.insert(0, site_packages_path)

        from shared_code.data import get_connection, return_connection

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            total = 0.0
            for item in items:
                sku = item.get("sku")
                qty_collected = item.get("qty_collected", item.get("qty", 1))

                if not sku:
                    logging.warning("Item %s has no SKU, skipping price lookup", item.get("id"))
                    continue

                # Query product price from database
                cursor.execute("""
                    SELECT price
                    FROM spar.products
                    WHERE sku = %s
                """, (sku,))

                result = cursor.fetchone()
                if result:
                    price = result[0]
                    total += price * qty_collected
                else:
                    logging.warning("No price found for SKU %s", sku)

            return round(total, 2)

        finally:
            if conn:
                return_connection(conn)

    except Exception as e:
        logging.error("Error calculating total amount: %s", e)
        return 0.0
