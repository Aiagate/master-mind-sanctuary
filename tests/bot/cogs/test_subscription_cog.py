from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
from discord.ext import commands

from app.bot.cogs.subscription_cog import SubscriptionCog


@pytest.fixture
def bot() -> MagicMock:
    return MagicMock(spec=commands.Bot)


@pytest.fixture
def cog(bot: MagicMock) -> SubscriptionCog:
    return SubscriptionCog(bot)


@pytest.fixture
def ctx() -> MagicMock:
    context = MagicMock(spec=commands.Context)
    context.author = MagicMock(spec=discord.Member)
    context.author.mention = "@user"
    context.author.send = AsyncMock()
    context.send = AsyncMock()
    return context


@pytest.mark.asyncio
async def test_subscribe_command_sends_dm_and_notifies(
    cog: SubscriptionCog, ctx: MagicMock
) -> None:
    # Act
    await cog.subscribe.callback(cog, ctx)  # pyright: ignore[reportCallIssue]

    # Assert
    ctx.author.send.assert_called_once()
    assert "Master-Mind-Sanctuary へようこそ！" in ctx.author.send.call_args[0][0]
    ctx.send.assert_called_once()
    assert "DMを送りました" in ctx.send.call_args[0][0]


@pytest.mark.asyncio
async def test_subscribe_command_handles_forbidden(
    cog: SubscriptionCog, ctx: MagicMock
) -> None:
    # Arrange
    ctx.author.send.side_effect = discord.Forbidden(MagicMock(), "Forbidden")

    # Act
    await cog.subscribe.callback(cog, ctx)  # pyright: ignore[reportCallIssue]

    # Assert
    ctx.author.send.assert_called_once()
    ctx.send.assert_called_once()
    assert "DMを送れませんでした" in ctx.send.call_args[0][0]


@pytest.mark.asyncio
async def test_subscribe_command_handles_unexpected_error(
    cog: SubscriptionCog, ctx: MagicMock
) -> None:
    # Arrange
    ctx.author.send.side_effect = Exception("Unexpected Error")

    # Act
    await cog.subscribe.callback(cog, ctx)  # pyright: ignore[reportCallIssue]

    # Assert
    ctx.author.send.assert_called_once()
    ctx.send.assert_called_once()
    assert "エラーが発生しました: Unexpected Error" in ctx.send.call_args[0][0]
