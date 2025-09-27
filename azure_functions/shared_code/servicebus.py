from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

from azure.servicebus import ServiceBusClient, ServiceBusMessage

_CONNECTION = os.getenv("SERVICEBUS_CONNECTION")
_QUEUE_NAME = os.getenv("SERVICEBUS_QUEUE_NAME", "list-updates")


def publish_event(payload: Dict[str, Any]) -> None:
    if not _CONNECTION:
        logging.info("SERVICEBUS_CONNECTION missing; skipping publish")
        return
    try:
        with ServiceBusClient.from_connection_string(_CONNECTION) as client:
            with client.get_queue_sender(queue_name=_QUEUE_NAME) as sender:
                sender.send_messages(ServiceBusMessage(json.dumps(payload, ensure_ascii=False)))
    except Exception:
        logging.exception("Failed to publish Service Bus message")
