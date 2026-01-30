"""Session aggregate root."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Self

from app.core.result import Err, Ok, Result
from app.domain.value_objects.session_id import SessionId


@dataclass
class Session:
    """Session aggregate.

    Represents a shell session.
    """

    _id: SessionId
    _created_at: datetime

    @classmethod
    def create(cls) -> Result[Self, Exception]:
        """Create a new Session.

        Returns:
            Result containing the new Session or an error.
        """
        id_result = SessionId.generate()
        if isinstance(id_result, Err):
            return Err(id_result.error)

        return Ok(
            cls(
                _id=id_result.unwrap(),
                _created_at=datetime.now(UTC),
            )
        )

    @classmethod
    def reconstruct(
        cls,
        id: SessionId,
        created_at: datetime,
    ) -> "Session":
        """Reconstruct an existing Session from persistence.

        Args:
            id: The existing ID.
            created_at: The creation timestamp.

        Returns:
            Reconstructed Session.
        """
        return cls(
            _id=id,
            _created_at=created_at,
        )

    @property
    def id(self) -> SessionId:
        """Get the ID."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._created_at
