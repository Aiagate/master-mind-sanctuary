from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from discord.ext import commands

from app.bot.cogs.brain_cog import BrainCog
from app.core.result import Ok
from app.domain.interfaces.event_bus import Event, IEventBus
from app.usecases.messaging.publish_received_direct_message import (
    PublishReceivedDirectMessageCommand,
)
from app.usecases.messaging.publish_received_message import (
    PublishReceivedMessageCommand,
)


@pytest.fixture
def bot() -> MagicMock:
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def bus() -> MagicMock:
    return MagicMock(spec=IEventBus)


@pytest.fixture
def cog(bot: MagicMock, bus: MagicMock) -> BrainCog:
    return BrainCog(bot, bus)


@pytest.fixture
def message() -> MagicMock:
    msg = MagicMock(spec=discord.Message)
    msg.author = MagicMock(spec=discord.User)
    msg.author.bot = False
    msg.author.name = "test_user"
    msg.content = "Hello"
    msg.channel = MagicMock(spec=discord.TextChannel)
    msg.channel.id = 123456789
    return msg


@pytest.mark.asyncio
async def test_on_message_publishes_command(cog: BrainCog, message: MagicMock) -> None:
    # Arrange
    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        # Act
        await cog.on_message(message)

        # Assert
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        command = args[0]
        assert isinstance(command, PublishReceivedMessageCommand)
        assert command.author == "test_user"
        assert command.content == "Hello"
        assert command.channel_id == 123456789


@pytest.mark.asyncio
async def test_on_message_ignores_bot(cog: BrainCog, message: MagicMock) -> None:
    # Arrange
    message.author.bot = True
    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        # Act
        await cog.on_message(message)

        # Assert
        mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_ignores_command(cog: BrainCog, message: MagicMock) -> None:
    # Arrange
    message.content = "/help"
    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        # Act
        await cog.on_message(message)

        # Assert
        mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_handles_dm(cog: BrainCog, message: MagicMock) -> None:
    # Arrange
    message.channel = MagicMock(spec=discord.DMChannel)
    message.channel.id = 987654321
    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        # Act
        await cog.on_message(message)

        # Assert
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        command = args[0]
        assert isinstance(command, PublishReceivedDirectMessageCommand)
        assert command.author == "test_user"
        assert command.content == "Hello"
        assert command.channel_id == 987654321


@pytest.mark.asyncio
async def test_on_sns_update_sends_message(cog: BrainCog, bot: MagicMock) -> None:
    # Arrange
    event = MagicMock(spec=Event)
    event.payload = {"key": "value"}

    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_channel.send = AsyncMock()
    bot.get_channel.return_value = mock_channel

    # Use real Ok result object
    mock_result = Ok(MagicMock(content="Update arrived"))

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog.on_sns_update(event)

        # Assert
        mock_send.assert_called_once()
        mock_channel.send.assert_called_once_with("Update arrived")


@pytest.mark.asyncio
async def test_on_heartbeat_sends_message(cog: BrainCog, bot: MagicMock) -> None:
    # Arrange
    event = MagicMock(spec=Event)

    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_channel.send = AsyncMock()
    bot.get_channel.return_value = mock_channel

    # Use real Ok result object
    mock_result = Ok(MagicMock(channel_id="123", content="Heartbeat response"))

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog.on_heartbeat(event)

        # Assert
        mock_send.assert_called_once()
        mock_channel.send.assert_called_once_with("Heartbeat response")
