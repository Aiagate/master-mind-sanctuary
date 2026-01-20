"""Tests for infrastructure Unit of Work component."""

import pytest

from app.core.result import is_ok
from app.domain.repositories import IUnitOfWork
from tests.infrastructure.helpers import TestEntity, TestId


@pytest.mark.asyncio
async def test_uow_rollback(uow: IUnitOfWork) -> None:
    """Test that the Unit of Work rolls back transactions on error."""
    user = TestEntity.create(
        name="Rollback Test",
        email="rollback@example.com",
    )
    initial_user = None

    # 1. Save a user and get its ID
    async with uow:
        repo = uow.GetRepository(TestEntity, TestId)
        save_result = await repo.add(user)
        assert is_ok(save_result)
        initial_user = save_result.value
        assert initial_user.id  # ULID should exist
        commit_result = await uow.commit()
        assert is_ok(commit_result)

    # 2. Attempt to update the user in a failing transaction
    try:
        async with uow:
            repo = uow.GetRepository(TestEntity, TestId)
            get_result = await repo.get_by_id(initial_user.id)
            assert is_ok(get_result)
            user_to_update = get_result.value

            # Use updated instance
            updated_instance = user_to_update.change_email("updated@example.com")

            await repo.update(updated_instance)
            raise ValueError("Simulating a failure")
    except ValueError:
        # Expected failure
        pass

    # 3. Verify that the email was NOT updated (rollback worked)
    async with uow:
        repo = uow.GetRepository(TestEntity, TestId)
        retrieved_result = await repo.get_by_id(initial_user.id)
        assert is_ok(retrieved_result)
        retrieved_user = retrieved_result.value
        assert retrieved_user.email == "rollback@example.com"
