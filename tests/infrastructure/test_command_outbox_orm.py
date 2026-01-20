from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.orm_models.command_outbox_orm import CommandOutboxORM


@pytest.mark.asyncio
async def test_command_outbox_orm_sqlite(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        command = CommandOutboxORM(
            id=uuid4(),
            command_type="TEST_COMMAND",
            payload={"key": "value"},
            status="PENDING",
        )
        session.add(command)
        await session.commit()

        # Verify
        result = await session.get(CommandOutboxORM, command.id)
        assert result is not None
        assert result.command_type == "TEST_COMMAND"
        assert result.payload == {"key": "value"}
