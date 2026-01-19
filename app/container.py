"""Dependency injection container configuration."""

import injector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.interfaces.ai_service import IAIService, IEmbeddingService
from app.domain.interfaces.event_bus import IEventBus
from app.domain.repositories import IUnitOfWork
from app.infrastructure.orm_registry import init_orm_mappings
from app.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


class DatabaseModule(injector.Module):
    """Module for database-related dependencies."""

    @injector.provider
    def provide_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Provide session factory for creating database sessions."""
        from app.infrastructure import database

        if database._session_factory is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return database._session_factory

    @injector.provider
    def provide_unit_of_work(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> IUnitOfWork:
        """Provide Unit of Work implementation for transaction management."""
        return SQLAlchemyUnitOfWork(session_factory)


def configure(binder: injector.Binder) -> None:
    """Configure dependency injection bindings."""
    # Initialize ORM mappings
    init_orm_mappings()

    binder.install(DatabaseModule())
    binder.install(AIModule())
    binder.install(MessagingModule())


class AIModule(injector.Module):
    """Module for AI-related dependencies."""

    @injector.provider
    @injector.singleton
    def provide_ai_service(self) -> IAIService:
        """Provide AI service implementation based on environment variable."""
        import os

        provider = os.getenv("AI_PROVIDER", "mock").lower()

        if provider == "gemini":
            from app.infrastructure.services.gemini_service import GeminiService

            return GeminiService()
        elif provider in ("gpt", "openai"):
            from app.infrastructure.services.gpt_service import GptService

            return GptService()
        elif provider == "ollama":
            from app.infrastructure.services.ollama_service import OllamaService

            return OllamaService()
        elif provider == "ollama-openai":
            from app.infrastructure.services.ollama_openai_service import (
                OllamaOpenAIService,
            )

            return OllamaOpenAIService()

        from app.infrastructure.services.mock_ai_service import MockAIService

        return MockAIService()

    @injector.provider
    @injector.singleton
    def provide_embedding_service(self) -> IEmbeddingService:
        """Provide Embedding service implementation based on environment variable."""
        import os

        # Default to 'ollama' as per plan, or 'mock' if prefer safe default.
        # Plan says default 'ollama'.
        provider = os.getenv("EMBEDDING_PROVIDER", "mock").lower()

        if provider == "ollama":
            from app.infrastructure.services.ollama_embedding_service import (
                OllamaEmbeddingService,
            )

            return OllamaEmbeddingService()
        elif provider == "gemini":
            from app.infrastructure.services.gemini_embedding_service import (
                GeminiEmbeddingService,
            )

            return GeminiEmbeddingService()

        from app.infrastructure.services.mock_embedding_service import (
            MockEmbeddingService,
        )

        return MockEmbeddingService()


class MessagingModule(injector.Module):
    """Module for messaging-related dependencies."""

    @injector.provider
    @injector.singleton
    def provide_event_bus(self) -> IEventBus:
        """Provide Event Bus implementation."""
        from app.infrastructure.messaging.redis_event_bus import RedisEventBus

        return RedisEventBus()
