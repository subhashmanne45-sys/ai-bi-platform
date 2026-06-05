# streaming/producer.py
# ============================================================
# Kafka producer — streams sales events in real time.
# Run this alongside the ETL consumer to simulate live data.
# ============================================================

import json
import time
import random
import uuid
from datetime import datetime

from config import logger, settings

try:
    from kafka import KafkaProducer
    from kafka.errors import NoBrokersAvailable
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    logger.warning("kafka-python not installed. Streaming will be skipped.")


def get_producer():
    """Create and return a Kafka producer, or None if unavailable."""
    if not KAFKA_AVAILABLE:
        return None
    try:
        producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            retries=3,
        )
        logger.info(f"Connected to Kafka at {settings.kafka_bootstrap_servers}")
        return producer
    except NoBrokersAvailable:
        logger.warning("Kafka broker not available. Streaming disabled.")
        return None
    except Exception as e:
        logger.error(f"Kafka connection failed: {e}")
        return None


def build_sale_event() -> dict:
    """Build a single synthetic sale event payload."""
    categories = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports"]
    regions    = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Hyderabad"]

    category = random.choice(categories)
    price    = round(random.uniform(100, 50000), 2)
    qty      = random.randint(1, 5)
    discount = round(random.uniform(0, 0.25), 2)

    return {
        "event_id":       str(uuid.uuid4()),
        "event_type":     "sale",
        "transaction_id": str(uuid.uuid4())[:12].upper(),
        "customer_id":    str(uuid.uuid4())[:8].upper(),
        "product_id":     str(uuid.uuid4())[:8].upper(),
        "category":       category,
        "region":         random.choice(regions),
        "quantity":       qty,
        "unit_price":     price,
        "discount_pct":   discount,
        "revenue":        round(price * qty * (1 - discount), 2),
        "payment_method": random.choice(["UPI", "Credit Card", "Debit Card", "Cash on Delivery"]),
        "channel":        random.choice(["Online", "Mobile App", "In-Store"]),
        "status":         random.choice(["Completed", "Completed", "Completed", "Pending"]),
        "timestamp":      datetime.utcnow().isoformat(),
    }


def stream_sales_events(
    producer,
    topic: str,
    interval_seconds: float = 2.0,
    max_events: int = None,
):
    """
    Continuously publish sale events to Kafka.

    Args:
        producer:         KafkaProducer instance
        topic:            Kafka topic name
        interval_seconds: Delay between events
        max_events:       Stop after N events (None = run forever)
    """
    count = 0
    logger.info(f"Starting stream → topic '{topic}' every {interval_seconds}s")

    try:
        while True:
            event = build_sale_event()
            producer.send(topic, key=event["transaction_id"], value=event)
            count += 1

            logger.debug(
                f"[{count}] Sent: {event['category']} | "
                f"₹{event['revenue']:,.2f} | {event['region']}"
            )

            if max_events and count >= max_events:
                logger.info(f"Reached max_events={max_events}. Stopping.")
                break

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("Stream interrupted by user.")
    finally:
        producer.flush()
        producer.close()
        logger.info(f"Stream closed after {count} events.")


if __name__ == "__main__":
    producer = get_producer()
    if producer:
        stream_sales_events(
            producer,
            topic=settings.kafka_topic_sales,
            interval_seconds=settings.streaming_interval_seconds,
        )
    else:
        logger.warning("No Kafka producer available. Check broker is running.")
