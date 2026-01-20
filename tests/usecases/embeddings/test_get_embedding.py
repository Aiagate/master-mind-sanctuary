from typing import Any

import pytest

from app.core.result import Err, Ok, is_err
from app.domain.interfaces.ai_service import IEmbeddingService
from app.usecases.embeddings.get_embedding import (
    GetEmbeddingHandler,
    GetEmbeddingQuery,
)
from app.usecases.result import ErrorType, UseCaseError


@pytest.fixture
def mock_embedding_service(mocker: Any) -> IEmbeddingService:
    service = mocker.Mock(spec=IEmbeddingService)
    service.embed_text = mocker.AsyncMock(return_value=Ok([0.1, 0.2, 0.3]))
    return service


@pytest.mark.asyncio
async def test_get_embedding_success(mock_embedding_service: IEmbeddingService):
    """Test successful embedding generation."""
    handler = GetEmbeddingHandler(mock_embedding_service)
    text = "Hello Embedding"
    query = GetEmbeddingQuery(text=text)

    result = await handler.handle(query)

    assert not is_err(result)
    embedding_result = result.unwrap()
    assert embedding_result.embedding == [0.1, 0.2, 0.3]

    # Verify interaction
    mock_embedding_service.embed_text.assert_called_once_with(text)  # type: ignore


@pytest.mark.asyncio
async def test_get_embedding_empty_text(mock_embedding_service: IEmbeddingService):
    """Test validation error for empty text."""
    handler = GetEmbeddingHandler(mock_embedding_service)
    query = GetEmbeddingQuery(text="")

    result = await handler.handle(query)

    assert is_err(result)
    error = result.error
    assert isinstance(error, UseCaseError)
    assert error.type == ErrorType.VALIDATION_ERROR
    assert "Text cannot be empty" in error.message

    # Verify service not called
    mock_embedding_service.embed_text.assert_not_called()  # type: ignore


@pytest.mark.asyncio
async def test_get_embedding_service_failure(mock_embedding_service: IEmbeddingService):
    """Test handling of embedding service failure."""
    mock_embedding_service.embed_text.return_value = Err("API Error")  # type: ignore
    handler = GetEmbeddingHandler(mock_embedding_service)
    query = GetEmbeddingQuery(text="Some text")

    result = await handler.handle(query)

    assert is_err(result)
    error = result.error
    assert isinstance(error, UseCaseError)
    assert error.type == ErrorType.UNEXPECTED
    assert "Failed to generate embedding" in error.message
    assert "API Error" in error.message
