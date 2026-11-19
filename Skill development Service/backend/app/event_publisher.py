import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any

log = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "")

def publish_skill_event(event_type: str, payload: Dict[str, Any]):
    """
    Publish domain events to the NagrikSetu central message broker (RabbitMQ).
    Events are published strictly after database transaction commits.
    If RabbitMQ is unavailable or unconfigured, the call fails gracefully without crashing the API.
    """
    if not RABBITMQ_URL:
        log.info(f"Local environment: RabbitMQ URL not configured. Event '{event_type}' logged locally.")
        return

    try:
        import pika
        parameters = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange="nagriksetu.events", exchange_type="topic", durable=True)

        message_body = {
            "event_type": event_type,
            "producer_service": "skill-development-service",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            **payload
        }

        channel.basic_publish(
            exchange="nagriksetu.events",
            routing_key=f"skill.{event_type.lower()}",
            body=json.dumps(message_body),
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2)
        )
        connection.close()
        log.info(f"Successfully published RabbitMQ event: {event_type}")
    except Exception as exc:
        log.warning(f"RabbitMQ event {event_type} could not be delivered: {exc}")
