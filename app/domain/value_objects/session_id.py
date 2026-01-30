"""Session ID value object."""

from dataclasses import dataclass

from app.domain.value_objects.base_id import BaseId


@dataclass(frozen=True)
class SessionId(BaseId):
    """Value object for Session ID."""

    pass
