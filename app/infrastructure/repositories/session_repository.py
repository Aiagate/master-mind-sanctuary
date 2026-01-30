"""SQLAlchemy implementation of session repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.result import Err, Ok, Result, is_ok
from app.domain.aggregates.session import Session
from app.domain.repositories import RepositoryErrorType
from app.domain.repositories.session_repository import ISessionRepository
from app.domain.value_objects.session_id import SessionId
from app.infrastructure.repositories.generic_repository import GenericRepository


class SqlAlchemySessionRepository(
    GenericRepository[Session, SessionId], ISessionRepository
):
    """SQLAlchemy session repository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository."""
        super().__init__(session, Session, SessionId)

    async def save(self, session: Session) -> Result[Session, Exception]:
        """Save a session."""
        # Use add for creation
        return await self.add(session)

    async def find_by_id(self, id: SessionId) -> Result[Session | None, Exception]:
        """Find a session by its ID."""
        result = await self.get_by_id(id)

        if is_ok(result):
            return Ok(result.unwrap())

        error = result.error
        if error.type == RepositoryErrorType.NOT_FOUND:
            return Ok(None)

        return Err(error)
