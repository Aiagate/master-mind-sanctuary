from unittest.mock import AsyncMock, Mock

import pytest

from app.core.result import is_err
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.event_bus import IEventBus
from app.domain.repositories import IUnitOfWork
from app.usecases.messaging.publish_received_direct_message import (
    PublishReceivedDirectMessageCommand,
    PublishReceivedDirectMessageHandler,
)


@pytest.mark.anyio
async def test_publish_received_direct_message(uow: IUnitOfWork):
    """Test saving message and publishing direct message event."""
    mock_bus = Mock(spec=IEventBus)
    mock_bus.publish = AsyncMock()

    handler = PublishReceivedDirectMessageHandler(mock_bus, uow)
    command = PublishReceivedDirectMessageCommand(
        author="User1", content="Hello DM", channel_id=123
    )

    result = await handler.handle(command)

    assert not is_err(result)

    # Verify DB persistence
    async with uow:
        messages = (
            await uow.GetRepository(ChatMessage).get_recent_history(10)
        ).unwrap()
        assert len(messages) == 1
        assert messages[0].content == "Hello DM"
        assert messages[0].role == ChatRole.USER

    # Verify Event publishing
    mock_bus.publish.assert_called_once()
    topic, payload = mock_bus.publish.call_args[0]
    assert topic == "discord.direct_message"
    assert payload["content"] == "Hello DM"
    assert payload["author"] == "User1"
    assert payload["channel_id"] == 123
