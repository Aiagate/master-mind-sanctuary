from dataclasses import dataclass

from injector import inject

from app.core.mediator import Mediator, Request, RequestHandler
from app.core.result import Ok, Result, is_ok
from app.domain.interfaces.event_bus import IEventBus
from app.usecases.chat.spontaneous_dialog import SpontaneousDialogCommand
from app.usecases.result import UseCaseError


@dataclass(frozen=True)
class HandleHeartbeatResult:
    """Result data for HandleHeartbeat command."""

    pass


@dataclass
class HandleHeartbeatCommand(Request[Result[HandleHeartbeatResult, UseCaseError]]):
    """Command to handle system heartbeat."""

    pass


class HandleHeartbeatHandler(
    RequestHandler[HandleHeartbeatCommand, Result[HandleHeartbeatResult, UseCaseError]]
):
    """Handler for HandleHeartbeatCommand."""

    @inject
    def __init__(self, bus: IEventBus) -> None:
        self._bus = bus

    async def handle(
        self, request: HandleHeartbeatCommand
    ) -> Result[HandleHeartbeatResult, UseCaseError]:
        """Process heartbeat event."""
        # 30% chance to trigger spontaneous dialog
        # if random.random() > 0.3:
        #     return Ok(HandleHeartbeatResult())

        # Trigger spontaneous dialog
        result = await Mediator.send_async(SpontaneousDialogCommand())

        if is_ok(result):
            data = result.unwrap()
            # Publish event for Bot to serve
            await self._bus.publish(
                "bot.speak", {"content": data.content, "channel_id": data.channel_id}
            )

        return Ok(HandleHeartbeatResult())
