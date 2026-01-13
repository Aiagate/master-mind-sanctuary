"""Tests for the dependency injection container."""

import os
from unittest import mock

import injector
import pytest
from injector import Injector

from app import container
from app.container import AIModule
from app.domain.interfaces.ai_service import IAIService
from app.domain.repositories import IUnitOfWork
from app.infrastructure.services.gemini_service import GeminiService
from app.infrastructure.services.gpt_service import GptService
from app.infrastructure.services.mock_ai_service import MockAIService
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@pytest.mark.anyio
async def test_di_container_bindings(test_db_engine: None) -> None:
    """Test that the DI container is configured correctly."""
    injector = Injector([container.configure])

    # Test that requesting the IUnitOfWork interface returns the correct implementation
    uow_instance = injector.get(IUnitOfWork)

    assert isinstance(uow_instance, SQLAlchemyUnitOfWork)


@pytest.mark.anyio
async def test_di_container_ai_service_binding(test_db_engine: None) -> None:
    """Test that the IAIService is bound correctly."""
    from app.domain.interfaces.ai_service import IAIService
    from app.infrastructure.services.mock_ai_service import MockAIService

    injector = Injector([container.configure])
    ai_service = injector.get(IAIService)

    # assert isinstance(ai_service, GeminiService)
    assert isinstance(ai_service, MockAIService)


def test_ai_provider_switching() -> None:
    """Test AI provider switching based on environment variable."""
    # Default (Mock)
    with mock.patch.dict(os.environ, {}, clear=True):
        di_container = injector.Injector([AIModule()])
        assert isinstance(di_container.get(IAIService), MockAIService)

    # Gemini
    with mock.patch.dict(os.environ, {"AI_PROVIDER": "gemini"}):
        di_container = injector.Injector([AIModule()])
        assert isinstance(di_container.get(IAIService), GeminiService)

    # GPT
    with mock.patch.dict(os.environ, {"AI_PROVIDER": "gpt"}):
        di_container = injector.Injector([AIModule()])
        assert isinstance(di_container.get(IAIService), GptService)

    # Unknown -> Mock
    with mock.patch.dict(os.environ, {"AI_PROVIDER": "unknown"}):
        di_container = injector.Injector([AIModule()])
        assert isinstance(di_container.get(IAIService), MockAIService)
