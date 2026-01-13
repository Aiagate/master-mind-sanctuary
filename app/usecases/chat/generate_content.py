from dataclasses import dataclass
from datetime import UTC, datetime

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Err, Ok, Result, is_err
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.aggregates.system_instruction import SystemInstruction
from app.domain.interfaces.ai_service import IAIService
from app.domain.repositories.interfaces import IUnitOfWork
from app.domain.value_objects import SentAt
from app.usecases.result import ErrorType, UseCaseError


@dataclass(frozen=True)
class GenerateContentResult:
    """Result data for GenerateContent query."""

    content: str


@dataclass
class GenerateContentQuery(Request[Result[GenerateContentResult, UseCaseError]]):
    """Query to generate content from AI."""

    prompt: str | None = None


class GenerateContentHandler(
    RequestHandler[GenerateContentQuery, Result[GenerateContentResult, UseCaseError]]
):
    """Handler for GenerateContentQuery."""

    @inject
    def __init__(
        self,
        ai_service: IAIService,
        uow: IUnitOfWork,
    ) -> None:
        self._ai_service = ai_service
        self._uow = uow

    async def handle(
        self, request: GenerateContentQuery
    ) -> Result[GenerateContentResult, UseCaseError]:
        """Handle request."""

        # 1. Get history
        async with self._uow:
            histories_result = await self._uow.GetRepository(
                ChatMessage
            ).get_recent_history(limit=100)
            if is_err(histories_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED,
                        message="Failed to retrieve chat history",
                    )
                )
            histories = histories_result.unwrap()

            prompt = request.prompt
            if not prompt:
                if not histories:
                    return Err(
                        UseCaseError(
                            type=ErrorType.VALIDATION_ERROR,
                            message="No prompt provided and history is empty",
                        )
                    )
                last_msg = histories[-1]
                if last_msg.role == ChatRole.USER:
                    prompt = last_msg.content
                    histories = histories[:-1]
                else:
                    return Err(
                        UseCaseError(
                            type=ErrorType.VALIDATION_ERROR,
                            message="Last message is not from user, and no prompt provided",
                        )
                    )

            # 2. Call AI Service (External call, no DB transaction)
            # Fetch active system instruction
            instruction_result = await self._uow.GetRepository(
                SystemInstruction
            ).find_active_by_provider(self._ai_service.provider)
            if is_err(instruction_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED,
                        message=f"Failed to fetch system instruction: {instruction_result.error}",
                    )
                )
            active_instruction = instruction_result.unwrap()
            instruction_text = (
                active_instruction.instruction if active_instruction else None
            )

            result = await self._ai_service.generate_content(
                prompt, histories, system_instruction=instruction_text
            )
            if is_err(result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED,
                        message="Failed to generate content",
                    )
                )
            content = result.unwrap()

            # 3. Save chat history (Only Model response)
            model_msg = ChatMessage.create(
                role=ChatRole.MODEL,
                content=content,
                sent_at=SentAt.from_primitive(datetime.now(UTC)).expect(
                    "SentAt creation failed"
                ),
            )
            await self._uow.GetRepository(ChatMessage).add(model_msg)
            await self._uow.commit()

            return Ok(GenerateContentResult(content=content))
