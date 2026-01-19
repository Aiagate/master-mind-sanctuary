from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.result import Result
from app.domain.aggregates.chat_history import ChatMessage
from app.domain.value_objects.ai_provider import AIProvider


@dataclass(frozen=True)
class AIServiceError(Exception):
    """Represents an error from the AI service."""

    message: str

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True)
class EmbeddingServiceError(Exception):
    """Represents an error from the embedding service."""

    message: str

    def __str__(self) -> str:
        return self.message


class IAIService(ABC):
    """Interface for AI service."""

    @abstractmethod
    async def generate_content(
        self,
        prompt: str,
        history: list[ChatMessage],
        system_instruction: str | None = None,
    ) -> Result[str, AIServiceError]:
        """Generate content from prompt.

        Args:
            prompt: The input text prompt.
            prompt: The input text prompt.
            history: The chat history.
            system_instruction: Optional system instruction to override default.

        Returns:
            Result[str, AIServiceError]: generated content or error.
        """
        pass

    @abstractmethod
    async def initialize_ai_agent(self) -> None:
        """Initialize AI agent (e.g. setup caching)."""
        pass

    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        """Get the provider type."""
        pass


class IEmbeddingService(ABC):
    """Interface for embedding service."""

    @abstractmethod
    async def embed_text(self, text: str) -> Result[list[float], EmbeddingServiceError]:
        """Generate embedding for text.

        Args:
            text: The input text.

        Returns:
            Result[list[float], EmbeddingServiceError]: generated embedding or error.
        """
        pass

    @abstractmethod
    async def embed_query(
        self, query: str
    ) -> Result[list[float], EmbeddingServiceError]:
        """Generate embedding for query.

        Args:
            query: The input query.

        Returns:
            Result[list[float], EmbeddingServiceError]: generated embedding or error.
        """
        pass

    @property
    @abstractmethod
    def provider(self) -> AIProvider:
        """Get the provider type."""
        pass
