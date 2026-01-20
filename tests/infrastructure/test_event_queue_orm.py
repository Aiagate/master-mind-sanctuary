from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.orm_models.event_queue_orm import EventQueueORM


@pytest.mark.asyncio
async def test_event_queue_orm_sqlite(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        event = EventQueueORM(
            id=uuid4(), type="TEST_EVENT", payload={"data": "test"}, status="PENDING"
        )
        session.add(event)
        await session.commit()

        # Verify
        result = await session.get(EventQueueORM, event.id)
        assert result is not None
        assert result.type == "TEST_EVENT"
        assert result.payload == {"data": "test"}
