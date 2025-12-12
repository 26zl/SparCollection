from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

_CONNECTION: Optional[str] = os.getenv("SERVICEBUS_CONNECTION")
_QUEUE_NAME: str = os.getenv("SERVICEBUS_QUEUE_NAME", "list-updates")


def _get_safe_event_summary(payload: Dict[str, Any]) -> str:
    """Extract only non-sensitive metadata for logging"""
    event_type = payload.get("type", "unknown")
    list_id = payload.get("listId", "unknown")
    return f"type={event_type}, listId={list_id}"


def publish_event(payload: Dict[str, Any]) -> None:
    if not _CONNECTION:
        logging.info("SERVICEBUS_CONNECTION missing; skipping publish")
        return
    
    # Try to import and use Service Bus, fallback to logging if not available
    try:
        from azure.servicebus import ServiceBusClient, ServiceBusMessage
        
        # Use a very short timeout to avoid delays
        with ServiceBusClient.from_connection_string(_CONNECTION, connection_timeout=2) as client:
            with client.get_queue_sender(queue_name=_QUEUE_NAME) as sender:
                sender.send_messages(ServiceBusMessage(json.dumps(payload, ensure_ascii=False)))
                logging.info("Successfully published event to Service Bus.")
                
                # If this is a list-completed event, also send to payment queue
                if payload.get("type") == "list-completed":
                    publish_to_payment_queue(payload)
                    
    except ImportError:
        logging.warning("azure-servicebus not available; event not published (%s)", _get_safe_event_summary(payload))
    except Exception as e:
        # Don't let Service Bus errors slow down the main operation
        logging.warning("Service Bus publish failed (non-critical): %s", str(e))
        # Log event summary without sensitive data
        logging.info("Event not published (%s)", _get_safe_event_summary(payload))


def publish_to_payment_queue(payload: Dict[str, Any]) -> None:
    """Send completed list to payment queue for processing"""
    if not _CONNECTION:
        logging.info("SERVICEBUS_CONNECTION missing; skipping payment queue publish")
        return
        
    try:
        from azure.servicebus import ServiceBusClient, ServiceBusMessage
        
        with ServiceBusClient.from_connection_string(_CONNECTION, connection_timeout=2) as client:
            with client.get_queue_sender(queue_name="payment-queue") as sender:
                sender.send_messages(ServiceBusMessage(json.dumps(payload, ensure_ascii=False)))
                logging.info("Successfully sent list to payment queue.")
    except Exception as e:
        logging.warning("Failed to send to payment queue (non-critical): %s", str(e))
