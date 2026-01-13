"""ORM mapping registry initialization.

This module registers all domain-to-ORM mappings at application startup.
Import this module to ensure mappings are registered before using repositories.
"""

from app.domain.aggregates.chat_history import ChatMessage
from app.domain.aggregates.system_instruction import SystemInstruction
from app.infrastructure.orm_mapping import register_orm_mapping
from app.infrastructure.orm_models.chat_message_orm import ChatMessageORM
from app.infrastructure.orm_models.system_instruction_orm import SystemInstructionORM


def init_orm_mappings() -> None:
    """Initialize all ORM mappings.

    This function should be called once at application startup,
    before any repository operations.
    """
    register_orm_mapping(ChatMessage, ChatMessageORM)
    register_orm_mapping(SystemInstruction, SystemInstructionORM)
