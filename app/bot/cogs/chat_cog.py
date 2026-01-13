import asyncio
import inspect

import discord
from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog
from app.core.mediator import Mediator
from app.domain.decorators import event_listener
from app.domain.interfaces.event_bus import Event, IEventBus
from app.usecases.chat.generate_content import GenerateContentQuery


class ChatCog(BaseCog, name="Chat"):
    """Event-driven chat agent."""

    def __init__(self, bot: commands.Bot, bus: IEventBus) -> None:
        super().__init__(bot)
        self.bus = bus
        self.generating_tasks: dict[int, asyncio.Task[None]] = {}

        # --- Event Subscription ---
        for _, member in inspect.getmembers(self):
            if hasattr(member, "_event_bus_topic"):
                topic = member._event_bus_topic
                self.bus.subscribe(topic, member)

    @event_listener("discord.message")
    async def on_discord_message(self, event: Event) -> None:
        """Handle discord message event to trigger AI generation."""
        content = event.payload.get("content")
        channel_id_raw = event.payload.get("channel_id")

        if not content or not channel_id_raw or not isinstance(content, str):
            return

        channel_id = int(channel_id_raw)

        # Retrieve channel object
        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except discord.NotFound:
                return

        if not isinstance(channel, discord.abc.Messageable):
            return

        # --- Task Cancellation & Generation Logic ---

        # 1. Cancel existing generation task for this channel
        if channel_id in self.generating_tasks:
            task = self.generating_tasks[channel_id]
            if not task.done():
                task.cancel()

        # 2. Start new generation task
        task = asyncio.create_task(self._generate_reply(channel))
        self.generating_tasks[channel_id] = task

    async def _generate_reply(self, channel: discord.abc.Messageable) -> None:
        """Generates reply and sends it."""
        # Ensure we can get an ID
        channel_id = getattr(channel, "id", None)
        if channel_id is None:
            return

        try:
            async with channel.typing():
                # Generate content using history (prompt is None, so it uses DB history)
                request = GenerateContentQuery()
                result = await Mediator.send_async(request)
                response = result.unwrap().content

                await channel.send(response)
        except asyncio.CancelledError:
            # Task was cancelled, simply exit
            pass
        except Exception as e:
            # Handle other errors
            await channel.send(f"An error occurred: {e}")
        finally:
            # Clean up task from dictionary
            if (
                channel_id in self.generating_tasks
                and self.generating_tasks[channel_id] == asyncio.current_task()
            ):
                del self.generating_tasks[channel_id]
