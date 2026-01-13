import discord
from discord.ext import commands

from app.domain.decorators import event_listener
from app.domain.interfaces.event_bus import Event, IEventBus


class DirectMessageResponseCog(commands.Cog):
    """Cog to handle automated responses to direct messages."""

    def __init__(self, bot: commands.Bot, bus: IEventBus) -> None:
        self.bot = bot
        self.bus = bus
        # Subscribe to the direct message topic
        self.bus.subscribe("discord.direct_message", self.on_direct_message_received)

    @event_listener("discord.direct_message")
    async def on_direct_message_received(self, event: Event) -> None:
        """Respond with a fixed message when a DM is received."""
        channel_id = event.payload.get("channel_id")
        if not channel_id:
            return

        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except (discord.NotFound, discord.Forbidden):
                return

        if channel and isinstance(channel, discord.abc.Messageable):
            # 固定メッセージを返信
            await channel.send("DMを受け取りました！メッセージありがとうございます。")
