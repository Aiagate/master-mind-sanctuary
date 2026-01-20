import pytest
from pytest_mock import MockerFixture

from app.core.result import Err, Ok
from app.infrastructure.services.gemini_embedding_service import GeminiEmbeddingService


@pytest.mark.asyncio
async def test_gemini_embedding_service_embed_text_success(
    mocker: MockerFixture,
) -> None:
    """Test successful embedding generation."""
    # Mock genai.Client

    mock_client = mocker.MagicMock()
    mock_response = mocker.MagicMock()
    mock_embedding = mocker.MagicMock()
    mock_embedding.values = [0.1, 0.2, 0.3]
    mock_response.embeddings = [mock_embedding]

    # Setup async mock for embed_content
    mock_client.aio.models.embed_content = mocker.AsyncMock(return_value=mock_response)

    def mock_getenv(key: str, default: str | None = None) -> str | None:
        if key == "GEMINI_API_KEY":
            return "fake_key"
        return default

    mocker.patch("google.genai.Client", return_value=mock_client)
    mocker.patch("os.getenv", side_effect=mock_getenv)

    service = GeminiEmbeddingService()
    result = await service.embed_text("hello world")

    assert isinstance(result, Ok)
    assert result.unwrap() == [0.1, 0.2, 0.3]
    mock_client.aio.models.embed_content.assert_called_once_with(
        model="text-embedding-004", contents="hello world"
    )


@pytest.mark.asyncio
async def test_gemini_embedding_service_no_key(mocker: MockerFixture) -> None:
    def mock_getenv(key: str, default: str | None = None) -> str | None:
        if key == "GEMINI_API_KEY":
            return None
        return default

    mocker.patch("os.getenv", side_effect=mock_getenv)

    service = GeminiEmbeddingService()
    result = await service.embed_text("hello world")

    assert isinstance(result, Err)
    assert "API key not configured" in str(result.error)


@pytest.mark.asyncio
async def test_gemini_embedding_service_api_error(mocker: MockerFixture) -> None:
    mock_client = mocker.MagicMock()
    mock_client.aio.models.embed_content = mocker.AsyncMock(
        side_effect=Exception("API Failure")
    )

    def mock_getenv(key: str, default: str | None = None) -> str | None:
        if key == "GEMINI_API_KEY":
            return "fake_key"
        return default

    mocker.patch("google.genai.Client", return_value=mock_client)
    mocker.patch("os.getenv", side_effect=mock_getenv)

    service = GeminiEmbeddingService()
    result = await service.embed_text("hello world")

    assert isinstance(result, Err)
    assert "Gemini Embedding Error: API Failure" in str(result.error)
