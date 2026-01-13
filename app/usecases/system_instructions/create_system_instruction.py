"""Use case to create a new system instruction."""

from dataclasses import dataclass

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Err, Ok, Result, is_err
from app.domain.aggregates.system_instruction import SystemInstruction
from app.domain.repositories.interfaces import IUnitOfWork
from app.domain.value_objects.ai_provider import AIProvider
from app.domain.value_objects.system_instruction_id import SystemInstructionId
from app.usecases.result import ErrorType, UseCaseError


@dataclass(frozen=True)
class CreateSystemInstructionResult:
    """Result data for CreateSystemInstruction command."""

    id: SystemInstructionId


@dataclass(frozen=True)
class CreateSystemInstructionCommand(
    Request[Result[CreateSystemInstructionResult, UseCaseError]]
):
    """Command to create a new system instruction."""

    provider: str
    instruction: str
    is_active: bool = False


class CreateSystemInstructionHandler(
    RequestHandler[
        CreateSystemInstructionCommand,
        Result[CreateSystemInstructionResult, UseCaseError],
    ]
):
    """Handler for CreateSystemInstructionCommand."""

    @inject
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, request: CreateSystemInstructionCommand
    ) -> Result[CreateSystemInstructionResult, UseCaseError]:
        """Execute the use case."""
        provider_result = AIProvider.from_primitive(request.provider)
        if is_err(provider_result):
            return Err(
                UseCaseError(
                    type=ErrorType.VALIDATION_ERROR,
                    message=str(provider_result.error),
                )
            )
        provider = provider_result.unwrap()

        async with self._uow:
            repo = self._uow.GetRepository(SystemInstruction)

            # If setting as active, deactivate current active instruction
            if request.is_active:
                active_result = await repo.find_active_by_provider(provider)
                if is_err(active_result):
                    return Err(
                        UseCaseError(
                            type=ErrorType.UNEXPECTED,
                            message=f"Failed to fetch active instruction: {active_result.error}",
                        )
                    )

                active_instruction = active_result.unwrap()
                if active_instruction:
                    active_instruction.deactivate()
                    save_result = await repo.save(active_instruction)
                    if is_err(save_result):
                        return Err(
                            UseCaseError(
                                type=ErrorType.UNEXPECTED,
                                message=f"Failed to deactivate existing instruction: {save_result.error}",
                            )
                        )

            # Create new instruction
            create_result = SystemInstruction.create(
                provider=provider,
                instruction=request.instruction,
                is_active=request.is_active,
            )
            if is_err(create_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.VALIDATION_ERROR,
                        message=f"Failed to create instruction: {create_result.error}",
                    )
                )

            new_instruction = create_result.unwrap()

            # Save
            save_result = await repo.save(new_instruction)
            if is_err(save_result):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED,
                        message=f"Failed to save new instruction: {save_result.error}",
                    )
                )

            await self._uow.commit()

            return Ok(CreateSystemInstructionResult(id=new_instruction.id))
