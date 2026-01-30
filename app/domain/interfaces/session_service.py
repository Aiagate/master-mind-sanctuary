"""Session service interface."""

from abc import ABC, abstractmethod

from app.core.result import Result
from app.domain.value_objects.session_id import SessionId


class ISessionService(ABC):
    """Interface for session service."""

    @abstractmethod
    async def start_session(self, session_id: SessionId) -> Result[None, Exception]:
        """Start a new session with the given ID.

        Args:
            session_id: The ID of the session to start.

        Returns:
            Result indicating success or failure.
        """
        ...
