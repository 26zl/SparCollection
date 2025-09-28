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
    """Simulate payment processing for a completed shopping list"""
    
    list_id = payment_data.get("listId")
    shop_id = payment_data.get("shopId")
    completed_by = payment_data.get("completedBy")
    completed_at = payment_data.get("completedAt")
    items = payment_data.get("items", [])
    title = payment_data.get("title", "Unknown List")
    
    # Simulate payment validation
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
    
    # Simulate payment calculation
    total_amount = calculate_total_amount(payment_data)
    
    # Simulate payment processing delay
    import time
    time.sleep(0.1)  # Simulate processing time
    
    # Simulate payment success/failure (90% success rate)
    import random
    if random.random() < 0.9:
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
    else:
        return {
            "success": False,
            "error": "Payment gateway timeout",
            "transactionId": None
        }


def calculate_total_amount(payment_data: Dict[str, Any]) -> float:
    """Calculate total amount for the shopping list"""
    
    # Simulate item pricing (in real scenario, this would come from product catalog)
    base_price_per_item = 25.0  # Base price in NOK
    quantity_multiplier = 1.2   # Price increases with quantity
    
    # Get items from the payment data (if available)
    items = payment_data.get("items", [])
    
    if items:
        total = 0.0
        for item in items:
            qty = item.get("qty", 1)
            # Simulate pricing based on item name and quantity
            item_price = base_price_per_item * (1 + (qty - 1) * quantity_multiplier)
            total += item_price
        return round(total, 2)
    else:
        # Fallback: estimate based on list metadata
        return round(base_price_per_item * 3.5, 2)  # Average 3.5 items per list
