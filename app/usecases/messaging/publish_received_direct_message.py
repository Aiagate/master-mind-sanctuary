from dataclasses import dataclass
from datetime import UTC, datetime

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Err, Ok, Result, is_err
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.event_bus import IEventBus
from app.domain.repositories.interfaces import IUnitOfWork
from app.domain.value_objects import SentAt
from app.usecases.result import ErrorType, UseCaseError


@dataclass(frozen=True)
class PublishReceivedDirectMessageResult:
    """Result data for PublishReceivedDirectMessage command."""

    pass


@dataclass(frozen=True)
class PublishReceivedDirectMessageCommand(
    Request[Result[PublishReceivedDirectMessageResult, UseCaseError]]
):
    """Command to publish a received Discord direct message."""

    author: str
    content: str
    channel_id: int


class PublishReceivedDirectMessageHandler(
    RequestHandler[
        PublishReceivedDirectMessageCommand,
        Result[PublishReceivedDirectMessageResult, UseCaseError],
    ]
):
    """Handler for PublishReceivedDirectMessage command."""

    @inject
    def __init__(self, bus: IEventBus, uow: IUnitOfWork) -> None:
        self.bus = bus
        self._uow = uow

    async def handle(
        self, request: PublishReceivedDirectMessageCommand
    ) -> Result[PublishReceivedDirectMessageResult, UseCaseError]:
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
        # 2. Publish Event
        pub_result = await self.bus.publish(
            "discord.direct_message",
            {
                "author": request.author,
                "content": request.content,
                "channel_id": request.channel_id,
            },
        )
        if is_err(pub_result):
            return Err(
                UseCaseError(
                    type=ErrorType.UNEXPECTED,
                    message=f"Failed to publish event: {pub_result.error}",
                )
            )
        return Ok(PublishReceivedDirectMessageResult())
