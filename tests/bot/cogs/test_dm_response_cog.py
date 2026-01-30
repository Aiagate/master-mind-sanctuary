from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from discord.ext import commands

from app.bot.cogs.dm_response_cog import DirectMessageResponseCog
from app.domain.interfaces.event_bus import Event, IEventBus


@pytest.fixture
def bot() -> MagicMock:
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def bus() -> MagicMock:
    return MagicMock(spec=IEventBus)


@pytest.fixture
def cog(bot: MagicMock, bus: MagicMock) -> DirectMessageResponseCog:
    return DirectMessageResponseCog(bot, bus)


@pytest.fixture
def channel() -> MagicMock:
    mock = MagicMock(spec=discord.DMChannel)
    mock.id = 987654321
    mock.send = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_on_direct_message_received_sends_reply(
    cog: DirectMessageResponseCog, bot: MagicMock, channel: MagicMock
) -> None:
    # Arrange
    event = Event(
        topic="discord.direct_message",
        payload={"channel_id": channel.id},
    )
    bot.get_channel.return_value = channel

    # Act
    await cog.on_direct_message_received(event)

    # Assert
    channel.send.assert_called_once_with(
        "DMを受け取りました！メッセージありがとうございます。"
    )


@pytest.mark.asyncio
async def test_on_direct_message_received_fetches_channel_if_not_in_cache(
    cog: DirectMessageResponseCog, bot: MagicMock, channel: MagicMock
) -> None:
    # Arrange
    event = Event(
        topic="discord.direct_message",
        payload={"channel_id": channel.id},
    )
    bot.get_channel.return_value = None
    bot.fetch_channel = AsyncMock(return_value=channel)

    # Act
    await cog.on_direct_message_received(event)

    # Assert
    bot.fetch_channel.assert_called_once_with(channel.id)
    channel.send.assert_called_once_with(
        "DMを受け取りました！メッセージありがとうございます。"
    )


@pytest.mark.asyncio
async def test_on_direct_message_received_handles_not_found(
    cog: DirectMessageResponseCog, bot: MagicMock
) -> None:
    # Arrange
    event = Event(
        topic="discord.direct_message",
        payload={"channel_id": 999},
    )
    bot.get_channel.return_value = None
    bot.fetch_channel = AsyncMock(
        side_effect=discord.NotFound(MagicMock(), "Not Found")
    )

    # Act
    await cog.on_direct_message_received(event)

    # Assert
    bot.fetch_channel.assert_called_once_with(999)
    # Should exit gracefully without sending anything
