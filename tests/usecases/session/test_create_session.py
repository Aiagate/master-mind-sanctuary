"""Tests for CreateSessionHandler."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.result import Ok, is_ok
from app.domain.aggregates.session import Session
from app.domain.interfaces.session_service import ISessionService
from app.domain.repositories.interfaces import IUnitOfWork
from app.domain.repositories.session_repository import ISessionRepository
from app.usecases.session.create_session import (
    CreateSessionCommand,
    CreateSessionHandler,
)


@pytest.mark.asyncio
async def test_create_session_success():
    """Test successful creation of session."""
    # Arrange
    mock_uow = MagicMock(spec=IUnitOfWork)
    mock_uow.__aenter__.return_value = mock_uow
    mock_uow.__aexit__.return_value = None

    mock_repo = AsyncMock(spec=ISessionRepository)
    mock_repo.save.return_value = Ok(MagicMock(spec=Session))

    mock_uow.GetRepository.return_value = mock_repo
    mock_uow.commit = AsyncMock()

    mock_service = AsyncMock(spec=ISessionService)
    mock_service.start_session.return_value = Ok(None)

    handler = CreateSessionHandler(mock_uow, mock_service)

    # Act
    result = await handler.handle(CreateSessionCommand())

    # Assert
    assert is_ok(result)
    session_id = result.unwrap()
    assert session_id is not None

    mock_uow.GetRepository.assert_called_with(Session)
    mock_repo.save.assert_called_once()
    mock_service.start_session.assert_called_once()
    mock_uow.commit.assert_called_once()
