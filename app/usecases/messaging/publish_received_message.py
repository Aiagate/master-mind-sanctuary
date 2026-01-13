from dataclasses import dataclass
from datetime import UTC, datetime

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Ok, Result
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.event_bus import IEventBus
from app.domain.repositories.interfaces import IUnitOfWork
from app.domain.value_objects import SentAt
from app.usecases.result import UseCaseError


@dataclass(frozen=True)
class PublishReceivedMessageResult:
    """Result data for PublishReceivedMessage command."""

    pass


@dataclass(frozen=True)
class PublishReceivedMessageCommand(
    Request[Result[PublishReceivedMessageResult, UseCaseError]]
):
    """Command to publish a received Discord message."""

    author: str
    content: str
    channel_id: int


class PublishReceivedMessageHandler(
    RequestHandler[
        PublishReceivedMessageCommand,
        Result[PublishReceivedMessageResult, UseCaseError],
    ]
):
    """Handler for PublishReceivedMessage command."""

    @inject
    def __init__(self, bus: IEventBus, uow: IUnitOfWork) -> None:
        self.bus = bus
        self._uow = uow

    async def handle(
        self, request: PublishReceivedMessageCommand
    ) -> Result[PublishReceivedMessageResult, UseCaseError]:
        """Save message and publish to EventBus."""
        # 1. Save to Database
        async with self._uow:
            user_msg = ChatMessage.create(
                role=ChatRole.USER,
                content=request.content,
                sent_at=SentAt.from_primitive(datetime.now(UTC)).expect(
                    "SentAt creation failed"
                ),
            )
            await self._uow.GetRepository(ChatMessage).add(user_msg)
            await self._uow.commit()

        # 2. Publish Event
        await self.bus.publish(
            "discord.message",
            {
                "author": request.author,
                "content": request.content,
                "channel_id": request.channel_id,
            },
        )
        return Ok(PublishReceivedMessageResult())
