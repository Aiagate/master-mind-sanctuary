from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord.ext import commands

from app.bot.cogs.system_instruction_cog import SystemInstructionCog
from app.core.result import Err, Ok


@pytest.fixture
def bot() -> MagicMock:
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def cog(bot: MagicMock) -> SystemInstructionCog:
    return SystemInstructionCog(bot)


@pytest.fixture
def ctx() -> MagicMock:
    context = MagicMock(spec=commands.Context)
    context.send = AsyncMock()
    context.command = MagicMock()
    return context


@pytest.mark.asyncio
async def test_create_instruction_command_success(
    cog: SystemInstructionCog, ctx: MagicMock
) -> None:
    # Arrange
    provider = "Gemini"
    instruction = "You are a cat."
    mock_result = Ok(MagicMock(id=123))

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog.create_instruction.callback(
            cog,
            ctx,
            provider,  # pyright: ignore
            instruction=instruction,  # pyright: ignore
        )

        # Assert
        mock_send.assert_called_once()
        ctx.send.assert_called_once_with("システム指示を作成しました。ID: 123")


@pytest.mark.asyncio
async def test_create_instruction_command_failure(
    cog: SystemInstructionCog, ctx: MagicMock
) -> None:
    # Arrange
    provider = "Gemini"
    instruction = "You are a cat."
    mock_error = MagicMock()
    mock_error.message = "Database Error"
    mock_result = Err(mock_error)

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog.create_instruction.callback(
            cog,
            ctx,
            provider,  # pyright: ignore
            instruction=instruction,  # pyright: ignore
        )

        # Assert
        mock_send.assert_called_once()
        ctx.send.assert_called_once_with("指示の作成に失敗しました: Database Error")
