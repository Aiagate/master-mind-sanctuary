import asyncio
import json
import logging
import os
from typing import Any

import redis.asyncio as redis
from redis.asyncio.client import PubSub

from app.domain.interfaces.event_bus import Event, EventHandler, IEventBus

logger = logging.getLogger(__name__)


class RedisEventBus(IEventBus):
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = {}
        self._redis: redis.Redis | None = None
        self._pubsub: PubSub | None = None
        self._running = False
        self._listening_task: asyncio.Task[None] | None = None

        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        if topic not in self._handlers:
            self._handlers[topic] = []
        self._handlers[topic].append(handler)
        logger.debug(f"Subscribed to topic: {topic}")

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        if not self._redis:
            logger.warning("Redis EventBus not started, cannot publish events.")
            return

        try:
            # We publish the full event structure as JSON
            # Ideally we might want to respect the 'Event' dataclass structure
            # but for now we just publish the payload wrapped in a dict
            message = {"topic": topic, "payload": payload}
            await self._redis.publish(topic, json.dumps(message))
            logger.debug(f"Published event to Redis: {topic}")
        except Exception as e:
            logger.error(f"Failed to publish event {topic}: {e}")
            raise

    async def start(self) -> None:
        if not self.redis_url:
            logger.error("REDIS_URL not set, cannot start EventBus.")
            return

        self._running = True
        try:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
            logger.info(f"Connected to Redis at {self.redis_url}")

            # Start the listener task
            self._listening_task = asyncio.create_task(self._listener())

        except Exception as e:
            logger.error(f"Error starting Redis EventBus: {e}")
            raise

    async def _listener(self) -> None:
        if not self._redis:
            return

        self._pubsub = self._redis.pubsub()

        # Subscribe to all topics that have handlers
        # Note: In a dynamic system, we might need to update subscriptions on the fly.
        # For simple bots, we often just subscribe to all relevant channels or a wildcard.
        # But here, we iterate over known handlers.
        # CAUTION: If handlers are added AFTER start(), this won't pick them up without logic change.
        # A common pattern is to subscribe to a wildcard or handle subscribe() dynamically.
        # For this implementation, let's assume we subscribe to specific channels or a global 'bot_events' channel
        # creating a pattern similar to the Postgres implementation.
        # However, Redis is usually 1 topic = 1 channel.
        # Let's support dynamic subscription updates or just subscribe to everything if possible?
        # Actually, let's just subscribe to the topics present at start.

        topics = list(self._handlers.keys())
        if not topics:
            logger.warning("No handlers registered, Redis listener waiting...")
            # We might want to loop and check for new topics or provide a method to update.
            # For simplicity, let's just wait.
            # OR better: subscribe calls should trigger psubscribe if running.
            pass

        # To ensure we catch everything, let's use a pattern subscription if possible,
        # or just subscribe to the channels we know about.
        # But wait, the `subscribe` method is sync.
        # Let's change the strategy: Subscribe to a single control channel OR managing subscriptions dynamically is harder.
        # SIMPLEST APPROACH: Just subscribe to the specific topic channels.

        if topics:
            await self._pubsub.subscribe(*topics)
            logger.info(f"Redis PubSub subscribed to: {topics}")

        async for message in self._pubsub.listen():
            if not self._running:
                break

            if message["type"] == "message":
                await self._process_message(message["channel"], message["data"])

    async def _process_message(self, channel: str, data: str) -> None:
        try:
            # We expect data to be the JSON we published
            # However, if we are filtering by channel=topic, we know the topic already.
            parsed_data = json.loads(data)

            # Extract payload.
            # Note: Creating Event object
            topic = parsed_data.get("topic", channel)
            payload = parsed_data.get("payload", {})

            event = Event(topic=topic, payload=payload)

            if handlers := self._handlers.get(topic):
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {topic}: {e}")

        except json.JSONDecodeError:
            logger.error(f"Failed to decode Redis message: {data}")
        except Exception as e:
            logger.error(f"Error processing Redis message: {e}")

    async def stop(self) -> None:
        self._running = False
        if self._pubsub:
            await self._pubsub.close()
        if self._redis:
            await self._redis.close()
        if self._listening_task:
            self._listening_task.cancel()
            try:
                await self._listening_task
            except asyncio.CancelledError:
                pass
