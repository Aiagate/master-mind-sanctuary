from typing import Any

import pytest

from app.core.result import is_err
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.event_bus import IEventBus
from app.domain.repositories import IUnitOfWork
from app.usecases.messaging.publish_received_message import (
    PublishReceivedMessageCommand,
    PublishReceivedMessageHandler,
)


@pytest.mark.asyncio
async def test_publish_received_message(uow: IUnitOfWork, mocker: Any):
    """Test saving message and publishing event."""
    mock_bus = mocker.Mock(spec=IEventBus)
    mock_bus.publish = mocker.AsyncMock()

    handler = PublishReceivedMessageHandler(mock_bus, uow)
    command = PublishReceivedMessageCommand(
        author="User1", content="Hello", channel_id=123
    )

    result = await handler.handle(command)

    assert not is_err(result)

    # Verify DB persistence
    async with uow:
        messages = (
            await uow.GetRepository(ChatMessage).get_recent_history(10)
        ).unwrap()
        assert len(messages) == 1
        assert messages[0].content == "Hello"
        assert messages[0].role == ChatRole.USER

    # Verify Event publishing
    mock_bus.publish.assert_called_once()
    topic, payload = mock_bus.publish.call_args[0]
    assert topic == "discord.message"
    assert payload["content"] == "Hello"
    assert payload["author"] == "User1"
    assert payload["channel_id"] == 123
