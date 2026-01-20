from unittest.mock import AsyncMock, MagicMock

import pytest
from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog
from app.usecases.result import ErrorType, UseCaseError


@pytest.fixture
def bot() -> MagicMock:
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def cog(bot: MagicMock) -> BaseCog:
    return BaseCog(bot)


@pytest.fixture
def ctx() -> MagicMock:
    context = MagicMock(spec=commands.Context)
    context.command = MagicMock()
    context.command.qualified_name = "test_command"
    context.send = AsyncMock()
    context.send_help = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_base_cog_handles_use_case_error(cog: BaseCog, ctx: MagicMock) -> None:
    # Arrange
    error_message = "Valid use case error"
    error = MagicMock()
    error.original = UseCaseError(type=ErrorType.UNEXPECTED, message=error_message)

    # Act
    await cog.cog_command_error(ctx, error)

    # Assert
    ctx.send.assert_called_once_with(f"Error: {error_message}")


@pytest.mark.asyncio
async def test_base_cog_handles_missing_argument_error(
    cog: BaseCog, ctx: MagicMock
) -> None:
    # Arrange
    error = commands.MissingRequiredArgument(MagicMock())

    # Act
    await cog.cog_command_error(ctx, error)

    # Assert
    ctx.send_help.assert_called_once_with(ctx.command)


@pytest.mark.asyncio
async def test_base_cog_handles_unexpected_error(cog: BaseCog, ctx: MagicMock) -> None:
    # Arrange
    error = Exception("Unexpected")

    # Act
    await cog.cog_command_error(ctx, error)

    # Assert
    ctx.send.assert_called_once_with(
        "An unexpected error occurred. Please try again later."
    )
