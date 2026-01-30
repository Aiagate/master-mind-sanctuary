from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from discord.ext import commands

from app.bot.cogs.embedding_cog import EmbeddingCog
from app.core.result import Err, Ok
from app.domain.interfaces.ai_service import IEmbeddingService


@pytest.fixture
def bot() -> MagicMock:
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.injector = MagicMock()
    return mock_bot


@pytest.fixture
def cog(bot: MagicMock) -> EmbeddingCog:
    return EmbeddingCog(bot)


@pytest.fixture
def ctx() -> MagicMock:
    context = MagicMock(spec=commands.Context)
    context.send = AsyncMock()
    context.command = MagicMock()
    return context


@pytest.mark.asyncio
async def test_embedding_test_command_success(
    cog: EmbeddingCog, bot: MagicMock, ctx: MagicMock
) -> None:
    # Arrange
    text = "hello"
    mock_embedding = [0.1, 0.2, 0.3]
    mock_result = Ok(MagicMock(embedding=mock_embedding))

    mock_service = MagicMock(spec=IEmbeddingService)
    mock_service.provider = "TestProvider"
    bot.injector.get.return_value = mock_service

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog.test.callback(cog, ctx, text=text)  # pyright: ignore[reportCallIssue]

        # Assert
        mock_send.assert_called_once()
        ctx.send.assert_called_once()
        sent_message = ctx.send.call_args[0][0]
        assert "Embedding生成成功!" in sent_message
        assert "次元数: 3" in sent_message
        assert "Provider: TestProvider" in sent_message


@pytest.mark.asyncio
async def test_embedding_test_command_failure(
    cog: EmbeddingCog, ctx: MagicMock
) -> None:
    # Arrange
    text = "hello"
    # Create a mock error with a message attribute
    mock_error = MagicMock()
    mock_error.message = "API Error"
    mock_result = Err(mock_error)

    with patch(
        "app.core.mediator.Mediator.send_async", new_callable=AsyncMock
    ) as mock_send:
        mock_send.return_value = mock_result

        # Act
        await cog.test.callback(cog, ctx, text=text)  # pyright: ignore[reportCallIssue]

        # Assert
        mock_send.assert_called_once()
        ctx.send.assert_called_once_with("Embedding生成失敗: API Error")
