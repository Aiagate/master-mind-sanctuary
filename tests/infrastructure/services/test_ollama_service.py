from datetime import UTC, datetime
from typing import Any

import pytest

from app.core.result import is_err, is_ok
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.interfaces.ai_service import AIServiceError
from app.domain.value_objects.ai_provider import AIProvider
from app.domain.value_objects.sent_at import SentAt
from app.infrastructure.services.ollama_service import OllamaService


class TestOllamaService:
    @pytest.fixture
    def mock_ollama_client(self, mocker: Any) -> Any:
        mock = mocker.patch("app.infrastructure.services.ollama_service.AsyncClient")
        client_instance = mocker.AsyncMock()
        mock.return_value = client_instance
        return client_instance

    def test_provider_property(self) -> None:
        service = OllamaService()
        assert service.provider == AIProvider.OLLAMA

    @pytest.mark.asyncio
    async def test_generate_content_success(
        self, mock_ollama_client: Any, mocker: Any
    ) -> None:
        # Setup
        service = OllamaService()

        mock_response = mocker.AsyncMock()
        mock_response.message.content = "Ollama response"
        mock_ollama_client.chat.return_value = mock_response

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
        assert result.unwrap() == "Ollama response"

        mock_ollama_client.chat.assert_called_once()
        call_args = mock_ollama_client.chat.call_args
        assert call_args is not None
        call_kwargs = call_args.kwargs
        assert call_kwargs["model"] == "gemma3"  # Default model in code
        assert len(call_kwargs["messages"]) == 2  # History + prompt

    @pytest.mark.asyncio
    async def test_generate_content_empty_response(
        self, mock_ollama_client: Any, mocker: Any
    ) -> None:
        # Setup
        service = OllamaService()

        mock_response = mocker.AsyncMock()
        mock_response.message.content = ""
        mock_ollama_client.chat.return_value = mock_response

        # Execute
        result = await service.generate_content("Hi", [])

        # Verify
        assert is_err(result)
        assert isinstance(result.error, AIServiceError)
        assert str(result.error) == "Ollama returned empty content."

    @pytest.mark.asyncio
    async def test_generate_content_api_error(self, mock_ollama_client: Any) -> None:
        # Setup
        service = OllamaService()
        mock_ollama_client.chat.side_effect = Exception("API connection failed")

        # Execute
        result = await service.generate_content("Hi", [])

        # Verify
        assert is_err(result)
        assert isinstance(result.error, AIServiceError)
        assert "Ollama API Error" in str(result.error)
