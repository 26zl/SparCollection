from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

_CONNECTION: Optional[str] = os.getenv("SERVICEBUS_CONNECTION")
_QUEUE_NAME: str = os.getenv("SERVICEBUS_QUEUE_NAME", "list-updates")


def _redact_payload_for_logging(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow copy of payload with sensitive fields redacted for logging."""
    sensitive_keys = {"employeeId", "completedBy"}
    if not isinstance(payload, dict):
        return payload
    redacted = payload.copy()
    for key in sensitive_keys:
        if key in redacted:
            redacted[key] = "***REDACTED***"
    return redacted


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
                logging.info("Successfully published event to Service Bus: %s", payload.get("type", "unknown"))
                
                # If this is a list-completed event, also send to payment queue
                if payload.get("type") == "list-completed":
                    publish_to_payment_queue(payload)
                    
    except ImportError:
        logging.warning(
            "azure-servicebus not available; logging event instead: %s", 
            json.dumps(_redact_payload_for_logging(payload), ensure_ascii=False)
        )
    except Exception as e:
        # Don't let Service Bus errors slow down the main operation
        logging.warning("Service Bus publish failed (non-critical): %s", str(e))
        # Just log the event instead of failing
        logging.info(
            "Event logged instead: %s", 
            json.dumps(_redact_payload_for_logging(payload), ensure_ascii=False)
        )


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
