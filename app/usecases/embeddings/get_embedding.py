from dataclasses import dataclass

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Err, Ok, Result, is_err
from app.domain.interfaces.ai_service import IEmbeddingService
from app.usecases.result import ErrorType, UseCaseError


@dataclass(frozen=True)
class GetEmbeddingResult:
    """Result data for GetEmbedding query."""

    embedding: list[float]


@dataclass
class GetEmbeddingQuery(Request[Result[GetEmbeddingResult, UseCaseError]]):
    """Query to generate embedding for text."""

    text: str


class GetEmbeddingHandler(
    RequestHandler[GetEmbeddingQuery, Result[GetEmbeddingResult, UseCaseError]]
):
    """Handler for GetEmbeddingQuery."""

    @inject
    def __init__(
        self,
        embedding_service: IEmbeddingService,
    ) -> None:
        self._embedding_service = embedding_service

    async def handle(
        self, request: GetEmbeddingQuery
    ) -> Result[GetEmbeddingResult, UseCaseError]:
        """Handle request."""

        if not request.text:
            return Err(
                UseCaseError(
                    type=ErrorType.VALIDATION_ERROR,
                    message="Text cannot be empty",
                )
            )

        result = await self._embedding_service.embed_text(request.text)
        if is_err(result):
            return Err(
                UseCaseError(
                    type=ErrorType.UNEXPECTED,
                    message=f"Failed to generate embedding: {result.error}",
                )
            )

        embedding = result.unwrap()
        return Ok(GetEmbeddingResult(embedding=embedding))
