from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.infrastructure.orm_models.command_outbox_orm import CommandOutboxORM
from app.infrastructure.repositories.command_repository import (
    SQLAlchemyCommandRepository,
)


@pytest.mark.asyncio
async def test_command_repository_dequeue(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        # Arrange
        command1 = CommandOutboxORM(
            id=uuid4(),
            command_type="TYPE1",
            payload={"key": "1"},
            status="PENDING",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
        command2 = CommandOutboxORM(
            id=uuid4(),
            command_type="TYPE2",
            payload={"key": "2"},
            status="PENDING",
            created_at=datetime(2026, 1, 2, tzinfo=UTC),
        )
        session.add(command1)
        session.add(command2)
        await session.commit()

        repo = SQLAlchemyCommandRepository(session)

        # Act
        result = await repo.dequeue()

        # Assert
        assert result is not None
        assert result.id == command1.id
        assert result.type == "TYPE1"


@pytest.mark.asyncio
async def test_command_repository_dequeue_empty(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repo = SQLAlchemyCommandRepository(session)
        result = await repo.dequeue()
        assert result is None


@pytest.mark.asyncio
async def test_command_repository_complete(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        # Arrange
        cmd_id = uuid4()
        command = CommandOutboxORM(
            id=cmd_id, command_type="TYPE1", payload={}, status="PENDING"
        )
        session.add(command)
        await session.commit()

        repo = SQLAlchemyCommandRepository(session)

        # Act
        await repo.complete(cmd_id)
        await session.commit()

        # Assert
        updated = await session.get(CommandOutboxORM, cmd_id)
        assert updated is not None
        assert updated.status == "PROCESSED"
        assert updated.processed_at is not None


@pytest.mark.asyncio
async def test_command_repository_fail(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        # Arrange
        cmd_id = uuid4()
        command = CommandOutboxORM(
            id=cmd_id, command_type="TYPE1", payload={}, status="PENDING"
        )
        session.add(command)
        await session.commit()

        repo = SQLAlchemyCommandRepository(session)

        # Act
        await repo.fail(cmd_id)
        await session.commit()

        # Assert
        updated = await session.get(CommandOutboxORM, cmd_id)
        assert updated is not None
        assert updated.status == "FAILED"
