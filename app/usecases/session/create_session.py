"""Use case for creating a session."""

from dataclasses import dataclass

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Err, Ok, Result, is_err
from app.domain.aggregates.session import Session
from app.domain.interfaces.session_service import ISessionService
from app.domain.repositories.interfaces import IUnitOfWork
from app.domain.value_objects.session_id import SessionId
from app.usecases.result import ErrorType, UseCaseError


@dataclass(frozen=True)
class CreateSessionCommand(Request[Result[SessionId, UseCaseError]]):
    """Command to create a new session."""

    pass


@dataclass
class CreateSessionHandler(
    RequestHandler[CreateSessionCommand, Result[SessionId, UseCaseError]]
):
    """Handler to create and start a new session."""

    _uow: IUnitOfWork
    _service: ISessionService

    @inject
    def __init__(self, uow: IUnitOfWork, service: ISessionService) -> None:
        self._uow = uow
        self._service = service

    async def handle(
        self, request: CreateSessionCommand
    ) -> Result[SessionId, UseCaseError]:
        """Execute the use case.

        Returns:
            Result containing the new SessionId or an error.
        """
        async with self._uow:
            # 1. Create new session aggregate
            session_result = Session.create()
            if is_err(session_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED, message=str(session_result.error)
                    )
                )

            session = session_result.unwrap()

            # 2. Save session to repository
            repository = self._uow.GetRepository(Session)
            save_result = await repository.save(session)
            if is_err(save_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED, message=str(save_result.error)
                    )
                )

            # 3. Start shell session
            start_result = await self._service.start_session(session.id)
            if is_err(start_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED, message=str(start_result.error)
                    )
                )

            await self._uow.commit()

            return Ok(session.id)
