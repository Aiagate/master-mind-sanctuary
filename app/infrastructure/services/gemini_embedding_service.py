import logging
import os

from google import genai

from app.core.result import Err, Ok, Result
from app.domain.interfaces.ai_service import EmbeddingServiceError, IEmbeddingService
from app.domain.value_objects.ai_provider import AIProvider

logger = logging.getLogger(__name__)


class GeminiEmbeddingService(IEmbeddingService):
    """Implementation of Embedding service using Google Gemini."""

    @property
    def provider(self) -> AIProvider:
        return AIProvider.GEMINI

    def __init__(self) -> None:
        """Initialize Gemini client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            # GeminiService と同様に、APIキーがない場合は None を設定し、実行時にエラーを返す
            self._client = None
        else:
            self._client = genai.Client(api_key=api_key)

        self._model = os.getenv("GEMINI_EMBEDDING_MODEL", "text-embedding-004")

    async def embed_text(self, text: str) -> Result[list[float], EmbeddingServiceError]:
        """Generate embedding for text using Gemini API."""
        return await self._get_embedding(text)

    async def embed_query(
        self, query: str
    ) -> Result[list[float], EmbeddingServiceError]:
        """Generate embedding for query using Gemini API."""
        return await self._get_embedding(query)

    async def _get_embedding(
        self, input_text: str
    ) -> Result[list[float], EmbeddingServiceError]:
        """Core embedding logic using Gemini async client."""
        if not self._client:
            return Err(EmbeddingServiceError("Gemini API key not configured."))

        try:
            # Use async client for embedding
            response = await self._client.aio.models.embed_content(
                model=self._model,
                contents=input_text,
            )

            if response.embeddings and len(response.embeddings) > 0:
                # 取得できた最初の embedding を返す
                embedding = response.embeddings[0].values
                if embedding is None:
                    return Err(
                        EmbeddingServiceError(
                            "Received empty embedding values from Gemini API."
                        )
                    )
                return Ok(embedding)

            return Err(EmbeddingServiceError("No embedding received from Gemini API."))

        except Exception as e:
            logger.exception("Gemini Embedding Error")
            return Err(EmbeddingServiceError(f"Gemini Embedding Error: {str(e)}"))
