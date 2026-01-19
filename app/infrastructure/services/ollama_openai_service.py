import logging
import os

from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from app.core.result import Err, Ok, Result
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.ai_service import AIServiceError, IAIService
from app.domain.value_objects.ai_provider import AIProvider

logger = logging.getLogger(__name__)


class OllamaOpenAIService(IAIService):
    """Implementation of AI service using Ollama via OpenAI-compatible API."""

    @property
    def provider(self) -> AIProvider:
        return AIProvider.OLLAMA_OPENAI

    def __init__(self) -> None:
        """Initialize Ollama client with OpenAI base URL."""
        # Use a specific environment variable for OpenAI compatible base URL if provided,
        # otherwise append /v1 as it's common for OpenAI compatible APIs
        base_url = os.getenv("OLLAMA_OPENAI_BASE_URL")
        if not base_url:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            base_url = f"{ollama_url.rstrip('/')}/v1"

        self._model = os.getenv("OLLAMA_MODEL", "gemma3")

        # Ollama OpenAI compatible API doesn't need a real API key
        self._client = AsyncOpenAI(base_url=base_url, api_key="ollama")

    async def initialize_ai_agent(self) -> None:
        """Initialize AI agent."""
        pass

    async def generate_content(
        self,
        prompt: str,
        history: list[ChatMessage],
        system_instruction: str | None = None,
    ) -> Result[str, AIServiceError]:
        """Generate content from prompt using Ollama via OpenAI API."""
        try:
            messages: list[ChatCompletionMessageParam] = []

            if system_instruction:
                messages.append(
                    ChatCompletionSystemMessageParam(
                        role="system", content=system_instruction
                    )
                )

            for msg in history:
                if msg.role == ChatRole.USER:
                    messages.append(
                        ChatCompletionUserMessageParam(role="user", content=msg.content)
                    )
                else:
                    messages.append(
                        ChatCompletionAssistantMessageParam(
                            role="assistant", content=msg.content
                        )
                    )

            messages.append(ChatCompletionUserMessageParam(role="user", content=prompt))

            for message in messages:
                logger.debug(f"Message: {message}")

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                stream=False,
            )

            content = response.choices[0].message.content
            if content is None:
                return Err(AIServiceError("Ollama (OpenAI) returned empty content."))

            return Ok(content)

        except Exception as e:
            logger.exception("Ollama OpenAI API Error")
            return Err(AIServiceError(f"Ollama OpenAI API Error: {str(e)}"))
