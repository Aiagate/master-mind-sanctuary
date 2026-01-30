"""Tests for the dependency injection container."""

import os
from typing import Any

import injector
import pytest
from injector import Injector

from app import container
from app.container import AIModule
from app.domain.interfaces.ai_service import IAIService, IEmbeddingService
from app.domain.interfaces.event_bus import IEventBus
from app.domain.repositories import IUnitOfWork
from app.infrastructure.messaging.redis_event_bus import RedisEventBus
from app.infrastructure.services.gemini_embedding_service import GeminiEmbeddingService
from app.infrastructure.services.gemini_service import GeminiService
from app.infrastructure.services.gpt_service import GptService
from app.infrastructure.services.mock_ai_service import MockAIService
from app.infrastructure.services.mock_embedding_service import MockEmbeddingService
from app.infrastructure.services.ollama_embedding_service import OllamaEmbeddingService
from app.infrastructure.services.ollama_openai_service import OllamaOpenAIService
from app.infrastructure.services.ollama_service import OllamaService
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_di_container_bindings(test_db_engine: None) -> None:
    """Test that the DI container is configured correctly."""
    injector = Injector([container.configure])

    # Test that requesting the IUnitOfWork interface returns the correct implementation
    uow_instance = injector.get(IUnitOfWork)

    assert isinstance(uow_instance, SQLAlchemyUnitOfWork)


@pytest.mark.asyncio
async def test_di_container_ai_service_binding(test_db_engine: None) -> None:
    """Test that the IAIService is bound correctly."""
    from app.domain.interfaces.ai_service import IAIService
    from app.infrastructure.services.mock_ai_service import MockAIService

    injector = Injector([container.configure])
    ai_service = injector.get(IAIService)

    # assert isinstance(ai_service, GeminiService)
    assert isinstance(ai_service, MockAIService)


def test_ai_provider_switching(mocker: Any) -> None:
    """Test AI provider switching based on environment variable."""
    # Default (Mock)
    mocker.patch.dict(os.environ, {}, clear=True)
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IAIService), MockAIService)

    # Gemini
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "gemini"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IAIService), GeminiService)

    # GPT
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "gpt"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IAIService), GptService)

    # Ollama
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "ollama"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IAIService), OllamaService)

    # Ollama-OpenAI
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "ollama-openai"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IAIService), OllamaOpenAIService)

    # Unknown -> Mock
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "unknown"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IAIService), MockAIService)


def test_embedding_provider_switching(mocker: Any) -> None:
    """Test Embedding provider switching based on environment variable."""
    # Default (Mock)
    mocker.patch.dict(os.environ, {}, clear=True)
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IEmbeddingService), MockEmbeddingService)

    # Gemini
    mocker.patch.dict(os.environ, {"EMBEDDING_PROVIDER": "gemini"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IEmbeddingService), GeminiEmbeddingService)

    # Ollama
    mocker.patch.dict(os.environ, {"EMBEDDING_PROVIDER": "ollama"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IEmbeddingService), OllamaEmbeddingService)

    # Unknown -> Mock
    mocker.patch.dict(os.environ, {"EMBEDDING_PROVIDER": "unknown"})
    di_container = injector.Injector([AIModule()])
    assert isinstance(di_container.get(IEmbeddingService), MockEmbeddingService)


def test_messaging_module() -> None:
    """Test MessagingModule provides RedisEventBus."""
    from app.container import MessagingModule

    di_container = injector.Injector([MessagingModule()])
    event_bus = di_container.get(IEventBus)
    assert isinstance(event_bus, RedisEventBus)


def test_database_module_uninitialized(mocker: Any) -> None:
    """Test DatabaseModule raises RuntimeError when database is not initialized."""
    from app.container import DatabaseModule
    from app.infrastructure import database

    # Force uninitialized state
    mocker.patch.object(database, "_session_factory", None)
    di_container = injector.Injector([DatabaseModule()])
    with pytest.raises(RuntimeError, match="Database not initialized"):
        di_container.get(container.async_sessionmaker[container.AsyncSession])
