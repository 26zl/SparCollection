from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

_CONNECTION = os.getenv("SERVICEBUS_CONNECTION")
_QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "list-updates")


def publish_event(payload: Dict[str, Any]) -> None:
    if not _CONNECTION:
        logging.info("SERVICEBUS_CONNECTION missing; skipping publish")
        return
    
    # Try to import and use Service Bus, fallback to logging if not available
    try:
        from azure.servicebus import ServiceBusClient, ServiceBusMessage
        
        with ServiceBusClient.from_connection_string(_CONNECTION, connection_timeout=5) as client:
            with client.get_queue_sender(queue_name=_QUEUE_NAME) as sender:
                sender.send_messages(ServiceBusMessage(json.dumps(payload, ensure_ascii=False)))
                logging.info("Successfully published event to Service Bus: %s", payload.get("type", "unknown"))
    except ImportError:
        logging.warning("azure-servicebus not available; logging event instead: %s", json.dumps(payload))
    except Exception:
        logging.exception("Failed to publish Service Bus message")
