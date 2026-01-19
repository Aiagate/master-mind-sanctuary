import logging
import os

from ollama import AsyncClient

from app.core.result import Err, Ok, Result
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.ai_service import AIServiceError, IAIService
from app.domain.value_objects.ai_provider import AIProvider

logger = logging.getLogger(__name__)


class OllamaService(IAIService):
    """Implementation of AI service using Ollama via official ollama library."""

    @property
    def provider(self) -> AIProvider:
        return AIProvider.OLLAMA

    def __init__(self) -> None:
        """Initialize Ollama client."""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._model = os.getenv("OLLAMA_MODEL", "gemma3")
        self._client = AsyncClient(host=base_url)

    async def initialize_ai_agent(self) -> None:
        """Initialize AI agent."""
        pass

    async def generate_content(
        self,
        prompt: str,
        history: list[ChatMessage],
        system_instruction: str | None = None,
    ) -> Result[str, AIServiceError]:
        """Generate content from prompt using Ollama."""
        try:
            messages: list[dict[str, str]] = []

            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})

            for msg in history:
                role = "user" if msg.role == ChatRole.USER else "assistant"
                messages.append({"role": role, "content": msg.content})

            messages.append({"role": "user", "content": prompt})

            response = await self._client.chat(
                model=self._model,
                messages=messages,
                stream=False,
            )

            content = response.message.content
            if not content:
                return Err(AIServiceError("Ollama returned empty content."))

            return Ok(content)

        except Exception as e:
            logger.exception("Ollama API Error")
            return Err(AIServiceError(f"Ollama API Error: {str(e)}"))
