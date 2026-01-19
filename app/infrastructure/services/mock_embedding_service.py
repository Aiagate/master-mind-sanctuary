from app.core.result import Ok, Result
from app.domain.interfaces.ai_service import EmbeddingServiceError, IEmbeddingService
from app.domain.value_objects.ai_provider import AIProvider


class MockEmbeddingService(IEmbeddingService):
    """Mock implementation of Embedding service."""

    @property
    def provider(self) -> AIProvider:
        """Get the provider type."""
        return AIProvider.MOCK

    async def embed_text(self, text: str) -> Result[list[float], EmbeddingServiceError]:
        """Generate mock embedding (zeros)."""
        return Ok([0.0] * 768)

    async def embed_query(
        self, query: str
    ) -> Result[list[float], EmbeddingServiceError]:
        """Generate mock embedding (zeros)."""
        return Ok([0.0] * 768)
