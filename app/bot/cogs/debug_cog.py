import inspect
import json
import logging
import os

import discord
from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog
from app.domain.decorators import event_listener
from app.domain.interfaces.event_bus import Event, IEventBus

logger = logging.getLogger(__name__)


class DebugCog(BaseCog):
    def __init__(self, bot: commands.Bot, bus: IEventBus) -> None:
        super().__init__(bot)
        self.bus = bus
        self.debug_channel_id = os.getenv("DEBUG_CHANNEL_ID")

        # Event Subscription
        for _, member in inspect.getmembers(self):
            if hasattr(member, "_event_bus_topic"):
                topic = member._event_bus_topic
                self.bus.subscribe(topic, member)

    @commands.hybrid_group(name="sync")
    async def sync_tree(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sync the application command tree."""
        await ctx.bot.tree.sync()
        await ctx.send("Synced application commands.")

    @event_listener("*")
    async def on_any_event(self, event: Event) -> None:
        if not self.debug_channel_id:
            return

        try:
            channel_id = int(self.debug_channel_id)
            channel = self.bot.get_channel(channel_id)

            # If channel is not in cache, try fetching it
            if not channel:
                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except Exception as e:
                    logger.warning(f"Could not fetch debug channel {channel_id}: {e}")
                    return

            if isinstance(channel, discord.abc.Messageable):
                # Format payload helper to handle non-serializable objects if any
                payload_str = json.dumps(
                    event.payload, default=str, indent=2, ensure_ascii=False
                )

                heading = f"**Event Received:** `{event.topic}`"
                code_block = f"```json\n{payload_str}\n```"

                content = f"{heading}\n{code_block}"

                # Handle Discord 2000 character limit
                if len(content) > 2000:
                    # Truncate JSON to fit
                    # Available space is 2000 - len(heading) - len("\n```json\n\n```") - safety margin
                    available = 2000 - len(heading) - 20
                    truncated_json = payload_str[:available] + "... (truncated)"
                    content = f"{heading}\n```json\n{truncated_json}\n```"

                await channel.send(content)

        except ValueError:
            logger.error("Invalid DEBUG_CHANNEL_ID format.")
        except Exception as e:
            logger.error(f"Error sending debug event to Discord: {e}")
