import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from app.bot.cogs.chat_cog import ChatCog
from app.core.result import Ok
from app.domain.interfaces.event_bus import Event, IEventBus


@pytest.fixture
def bot() -> MagicMock:
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def bus() -> MagicMock:
    return MagicMock(spec=IEventBus)


@pytest.fixture
def cog(bot: MagicMock, bus: MagicMock) -> ChatCog:
    return ChatCog(bot, bus)


@pytest.fixture
def channel() -> MagicMock:
    mock = MagicMock(spec=discord.TextChannel)
    mock.id = 123456789
    mock.send = AsyncMock()
    mock.typing.return_value.__aenter__ = AsyncMock()
    mock.typing.return_value.__aexit__ = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_on_discord_message_triggers_reply(
    cog: ChatCog, bot: MagicMock, channel: MagicMock
) -> None:
    # Arrange
    event = Event(
        topic="discord.message",
        payload={"content": "Hello", "channel_id": str(channel.id)},
    )
    bot.get_channel.return_value = channel

    # Mock _generate_reply to avoid actual background task execution in this test
    with patch.object(cog, "_generate_reply", new_callable=AsyncMock) as mock_reply:
        # Act
        await cog.on_discord_message(event)

        # Assert
        mock_reply.assert_called_once_with(channel)
        assert channel.id in cog.generating_tasks


@pytest.mark.asyncio
async def test_generate_reply_sends_content(cog: ChatCog, channel: MagicMock) -> None:
    # Arrange
    mock_result = Ok(MagicMock(content="AI Response"))

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog._generate_reply(channel)

        # Assert
        mock_send.assert_called_once()
        channel.send.assert_called_once_with("AI Response")


@pytest.mark.asyncio
async def test_on_discord_message_cancels_previous_task(
    cog: ChatCog, bot: MagicMock, channel: MagicMock
) -> None:
    # Arrange
    event = Event(
        topic="discord.message",
        payload={"content": "Hello", "channel_id": str(channel.id)},
    )
    bot.get_channel.return_value = channel

    # Pre-populate a fake task
    previous_task = MagicMock(spec=asyncio.Task)
    previous_task.done.return_value = False
    cog.generating_tasks[channel.id] = previous_task

    with patch.object(cog, "_generate_reply", new_callable=AsyncMock):
        # Act
        await cog.on_discord_message(event)

        # Assert
        previous_task.cancel.assert_called_once()
