"""Use case to change active system instruction."""

from dataclasses import dataclass

from injector import inject

from app.core.mediator import Request, RequestHandler
from app.core.result import Err, Ok, Result
from app.domain.aggregates.system_instruction import SystemInstruction
from app.domain.repositories import IUnitOfWork
from app.domain.value_objects.system_instruction_id import SystemInstructionId
from app.usecases.result import ErrorType, UseCaseError


@dataclass(frozen=True)
class ChangeActiveSystemInstructionResult:
    """Result data for ChangeActiveSystemInstruction command."""

    pass


@dataclass(frozen=True)
class ChangeActiveSystemInstructionCommand(
    Request[Result[ChangeActiveSystemInstructionResult, UseCaseError]]
):
    """Command to change the active system instruction."""

    instruction_id: SystemInstructionId


class ChangeActiveSystemInstructionHandler(
    RequestHandler[
        ChangeActiveSystemInstructionCommand,
        Result[ChangeActiveSystemInstructionResult, UseCaseError],
    ]
):
    """Handler for ChangeActiveSystemInstructionCommand."""

    @inject
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, request: ChangeActiveSystemInstructionCommand
    ) -> Result[ChangeActiveSystemInstructionResult, UseCaseError]:
        """Execute the use case."""
        async with self._uow:
            repo = self._uow.GetRepository(SystemInstruction)

            # Find the instruction to activate
            target_result = await repo.find_by_id(request.instruction_id)
            if isinstance(target_result, Err):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED, message=str(target_result.error)
                    )
                )

            target_instruction = target_result.unwrap()
            if not target_instruction:
                return Err(
                    UseCaseError(
                        type=ErrorType.NOT_FOUND,
                        message=f"Instruction {request.instruction_id} not found",
                    )
                )

            # Find currently active instruction for this provider
            active_result = await repo.find_active_by_provider(
                target_instruction.provider
            )
            if isinstance(active_result, Err):
                return Err(
                    UseCaseError(
                        type=ErrorType.UNEXPECTED, message=str(active_result.error)
                    )
                )

            # Deactivate currently active one if exists and different
            active_instruction = active_result.unwrap()
            if active_instruction and active_instruction.id != target_instruction.id:
                active_instruction.deactivate()
                save_result = await repo.save(active_instruction)
                if isinstance(save_result, Err):
                    return Err(
                        UseCaseError(
                            type=ErrorType.UNEXPECTED, message=str(save_result.error)
                        )
                    )

            # Activate target
            if not target_instruction.is_active:
                target_instruction.activate()
                save_result = await repo.save(target_instruction)
                if isinstance(save_result, Err):
                    return Err(
                        UseCaseError(
                            type=ErrorType.UNEXPECTED, message=str(save_result.error)
                        )
                    )

            await self._uow.commit()

        return Ok(ChangeActiveSystemInstructionResult())
