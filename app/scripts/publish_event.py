import argparse
import asyncio
import json
import logging
import sys

from app.core.config import load_app_environment
from app.core.result import is_err, is_ok
from app.infrastructure.messaging.redis_event_bus import RedisEventBus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Publish an event to the EventBus.")
    parser.add_argument("event_type", help="The type/topic of the event to publish.")
    parser.add_argument(
        "payload", help="The JSON payload for the event.", type=str, default="{}"
    )

    args = parser.parse_args()

    # Load environment variables
    load_app_environment()

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        sys.exit(1)

    bus = RedisEventBus()

    logger.info("Starting EventBus...")
    start_result = await bus.start()
    if is_err(start_result):
        logger.error(f"Failed to start EventBus: {start_result.error}")
        sys.exit(1)

    logger.info(f"Publishing event: {args.event_type} with payload: {payload}")
    publish_result = await bus.publish(args.event_type, payload)

    if is_ok(publish_result):
        logger.info("Event published successfully.")
    else:
        logger.error(f"Failed to publish event: {publish_result.error}")

    logger.info("Stopping EventBus...")
    await bus.stop()


if __name__ == "__main__":
    asyncio.run(main())
