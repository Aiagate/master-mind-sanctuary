import logging
import os

from openai import AsyncOpenAI

from app.core.result import Err, Ok, Result
from app.domain.interfaces.ai_service import EmbeddingServiceError, IEmbeddingService
from app.domain.value_objects.ai_provider import AIProvider

logger = logging.getLogger(__name__)


class OllamaEmbeddingService(IEmbeddingService):
    """Implementation of Embedding service using Ollama via OpenAI-compatible API."""

    @property
    def provider(self) -> AIProvider:
        return AIProvider.OLLAMA_OPENAI

    def __init__(self) -> None:
        """Initialize Ollama client with OpenAI base URL."""
        base_url = os.getenv("OLLAMA_OPENAI_BASE_URL")
        if not base_url:
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            base_url = f"{base_url.rstrip('/')}/v1"

        self._model = os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma")

        # Ollama OpenAI compatible API doesn't need a real API key
        self._client = AsyncOpenAI(base_url=base_url, api_key="ollama")

    async def embed_text(self, text: str) -> Result[list[float], EmbeddingServiceError]:
        """Generate embedding for text using Ollama via OpenAI API."""
        return await self._get_embedding(text)

    async def embed_query(
        self, query: str
    ) -> Result[list[float], EmbeddingServiceError]:
        """Generate embedding for query using Ollama via OpenAI API."""
        return await self._get_embedding(query)

    async def _get_embedding(
        self, input_text: str
    ) -> Result[list[float], EmbeddingServiceError]:
        """Core embedding logic using OpenAI-compatible client."""
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=input_text,
            )
            embedding = response.data[0].embedding
            return Ok(embedding)
        except Exception as e:
            logger.exception("Ollama OpenAI Embedding Error")
            return Err(
                EmbeddingServiceError(f"Ollama OpenAI Embedding Error: {str(e)}")
            )
