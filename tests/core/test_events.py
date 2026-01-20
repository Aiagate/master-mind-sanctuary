from datetime import datetime

from app.core.events import AppEvent, EventType


def test_app_event_initialization():
    # Arrange
    event_type = EventType.USER_MESSAGE
    payload = {"message": "hello"}

    # Act
    event = AppEvent(type=event_type, payload=payload)

    # Assert
    assert event.type == event_type
    assert event.payload == payload
    assert isinstance(event.timestamp, datetime)


def test_app_event_default_payload():
    # Act
    event = AppEvent(type=EventType.HEARTBEAT)

    # Assert
    assert event.payload == {}
