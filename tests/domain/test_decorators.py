from typing import Any

from app.domain.decorators import event_listener


def test_event_listener_decorator_adds_attribute() -> None:
    # Arrange
    topic = "test.topic"

    # Act
    @event_listener(topic)
    def my_handler(event: Any) -> None:
        pass

    # Assert
    assert hasattr(my_handler, "_event_bus_topic")
    assert my_handler._event_bus_topic == topic  # pyright: ignore[reportFunctionMemberAccess]
