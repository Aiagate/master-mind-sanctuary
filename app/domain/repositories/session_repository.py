"""Session repository interface."""

from abc import ABC, abstractmethod

from app.core.result import Result
from app.domain.aggregates.session import Session
from app.domain.value_objects.session_id import SessionId


class ISessionRepository(ABC):
    """Interface for session repository."""

    @abstractmethod
    async def save(self, session: Session) -> Result[Session, Exception]:
        """Save a session.

        Args:
            session: The session to save.

        Returns:
            Result containing the saved session or an error.
        """
        ...

    @abstractmethod
    async def find_by_id(self, id: SessionId) -> Result[Session | None, Exception]:
        """Find a session by its ID.

        Args:
            id: The session ID.

        Returns:
            Result containing the session if found, None otherwise, or an error.
        """
        ...
