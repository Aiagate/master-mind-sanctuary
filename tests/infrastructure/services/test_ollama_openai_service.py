from datetime import UTC, datetime
from typing import Any

import pytest
from openai.types.chat import ChatCompletion

from app.core.result import is_err, is_ok
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.ai_service import AIServiceError
from app.domain.value_objects.ai_provider import AIProvider
from app.domain.value_objects.sent_at import SentAt
from app.infrastructure.services.ollama_openai_service import OllamaOpenAIService


class TestOllamaOpenAIService:
    @pytest.fixture
    def mock_openai_client(self, mocker: Any) -> Any:
        mock = mocker.patch(
            "app.infrastructure.services.ollama_openai_service.AsyncOpenAI"
        )
        client_instance = mocker.AsyncMock()
        mock.return_value = client_instance
        return client_instance

    def test_provider_property(self) -> None:
        service = OllamaOpenAIService()
        assert service.provider == AIProvider.OLLAMA_OPENAI

    @pytest.mark.asyncio
    async def test_generate_content_success(
        self, mock_openai_client: Any, mocker: Any
    ) -> None:
        # Setup
        service = OllamaOpenAIService()

        mock_response = mocker.MagicMock(spec=ChatCompletion)
        mock_choice = mocker.MagicMock()
        mock_choice.message.content = "Ollama OpenAI response"
        mock_response.choices = [mock_choice]

        mock_openai_client.chat.completions.create.return_value = mock_response

        history = [
            ChatMessage.create(
                role=ChatRole.USER,
                content="Hello",
                sent_at=SentAt.from_primitive(datetime.now(UTC)).unwrap(),
            )
        ]

        # Execute
        result = await service.generate_content("Hi there", history)

        # Verify
        assert is_ok(result)
        assert result.unwrap() == "Ollama OpenAI response"

        mock_openai_client.chat.completions.create.assert_called_once()
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args is not None
        call_kwargs = call_args.kwargs
        assert call_kwargs["model"] == "gemma3"
        assert len(call_kwargs["messages"]) == 2

    @pytest.mark.asyncio
    async def test_generate_content_empty_response(
        self, mock_openai_client: Any, mocker: Any
    ) -> None:
        # Setup
        service = OllamaOpenAIService()

        mock_response = mocker.MagicMock(spec=ChatCompletion)
        mock_choice = mocker.MagicMock()
        mock_choice.message.content = None
        mock_response.choices = [mock_choice]

        mock_openai_client.chat.completions.create.return_value = mock_response

        # Execute
        result = await service.generate_content("Hi", [])

        # Verify
        assert is_err(result)
        assert isinstance(result.error, AIServiceError)
        assert str(result.error) == "Ollama (OpenAI) returned empty content."

    @pytest.mark.asyncio
    async def test_generate_content_api_error(self, mock_openai_client: Any) -> None:
        # Setup
        service = OllamaOpenAIService()
        mock_openai_client.chat.completions.create.side_effect = Exception(
            "API connection failed"
        )

        # Execute
        result = await service.generate_content("Hi", [])

        # Verify
        assert is_err(result)
        assert isinstance(result.error, AIServiceError)
        assert "Ollama OpenAI API Error" in str(result.error)
