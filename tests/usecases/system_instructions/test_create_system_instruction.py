"""Tests for CreateSystemInstruction use case."""

from typing import Any

import pytest

from app.core.result import Err, is_err
from app.domain.aggregates.system_instruction import SystemInstruction
from app.domain.repositories import IUnitOfWork
from app.domain.repositories.interfaces import RepositoryError, RepositoryErrorType
from app.domain.value_objects.ai_provider import AIProvider
from app.usecases.result import ErrorType, UseCaseError
from app.usecases.system_instructions.create_system_instruction import (
    CreateSystemInstructionCommand,
    CreateSystemInstructionHandler,
)


@pytest.mark.asyncio
async def test_create_system_instruction_basic(uow: IUnitOfWork):
    """Test creating a simple system instruction."""
    handler = CreateSystemInstructionHandler(uow)
    command = CreateSystemInstructionCommand(
        provider=AIProvider.GEMINI.value,
        instruction="Basic instruction",
        is_active=False,
    )

    result = await handler.handle(command)
    assert not is_err(result)
    new_id = result.unwrap().id

    # Verify saved state
    async with uow:
        repo = uow.GetRepository(SystemInstruction)
        saved_instr = (await repo.find_by_id(new_id)).unwrap()
        assert saved_instr is not None
        assert saved_instr.provider == AIProvider.GEMINI
        assert saved_instr.instruction == "Basic instruction"
        assert not saved_instr.is_active


@pytest.mark.asyncio
async def test_create_system_instruction_active_switches_existing(uow: IUnitOfWork):
    """Test creating an active instruction switches off the existing one."""
    # Setup existing active instruction
    res1 = SystemInstruction.create(
        AIProvider.GEMINI, "Old Instruction", is_active=True
    )
    assert not is_err(res1)
    old_instr = res1.unwrap()

    async with uow:
        repo = uow.GetRepository(SystemInstruction)
        await repo.save(old_instr)
        await uow.commit()

    # Create new active instruction
    handler = CreateSystemInstructionHandler(uow)
    command = CreateSystemInstructionCommand(
        provider=AIProvider.GEMINI.value,
        instruction="New Instruction",
        is_active=True,
    )

    result = await handler.handle(command)
    assert not is_err(result)
    new_id = result.unwrap().id

    # Verify state
    async with uow:
        repo = uow.GetRepository(SystemInstruction)

        # Check old instruction is deactivated
        fetched_old = (await repo.find_by_id(old_instr.id)).unwrap()
        assert fetched_old is not None
        assert not fetched_old.is_active

        # Check new instruction is active
        fetched_new = (await repo.find_by_id(new_id)).unwrap()
        assert fetched_new is not None
        assert fetched_new.is_active
        assert fetched_new.instruction == "New Instruction"


@pytest.mark.asyncio
async def test_create_system_instruction_invalid_provider(uow: IUnitOfWork):
    """Test handling of invalid provider string."""
    handler = CreateSystemInstructionHandler(uow)
    command = CreateSystemInstructionCommand(
        provider="InvalidProvider",
        instruction="Instruction",
        is_active=False,
    )

    result = await handler.handle(command)

    assert is_err(result)
    assert isinstance(result.error, UseCaseError)
    assert result.error.type == ErrorType.VALIDATION_ERROR
    assert "Invalid AI provider" in str(result.error)


@pytest.mark.asyncio
async def test_create_system_instruction_repo_error(uow: IUnitOfWork, mocker: Any):
    """Test handling of repository errors during save."""
    # Create mock UoW and Repo
    mock_uow = mocker.Mock(spec=IUnitOfWork)
    mock_uow.__aenter__ = mocker.AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = mocker.AsyncMock(return_value=None)
    mock_uow.commit = mocker.AsyncMock()

    mock_repo = mocker.Mock()
    # Mock save to return error
    error = RepositoryError(RepositoryErrorType.UNEXPECTED, "DB Error")
    mock_repo.save = mocker.AsyncMock(return_value=Err(error))
    # Mock find_active_by_provider (needed for is_active checks, even if False is passed it might not be called,
    # but if CreateSystemInstructionHandler checks it only when True.
    # Let's assume is_active=False for simplicity in this error case)

    mock_uow.GetRepository.return_value = mock_repo

    handler = CreateSystemInstructionHandler(mock_uow)
    command = CreateSystemInstructionCommand(
        provider=AIProvider.GEMINI.value,
        instruction="Instruction",
        is_active=False,
    )

    result = await handler.handle(command)

    assert is_err(result)
    assert isinstance(result.error, UseCaseError)
    assert result.error.type == ErrorType.UNEXPECTED
    assert "DB Error" in str(result.error)
