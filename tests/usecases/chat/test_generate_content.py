from datetime import UTC, datetime
from typing import Any

import pytest

from app.core.result import Err, Ok, is_err
from app.domain.aggregates.chat_history import ChatMessage, ChatRole
from app.domain.aggregates.system_instruction import SystemInstruction
from app.domain.interfaces.ai_service import IAIService
from app.domain.repositories import IUnitOfWork
from app.domain.value_objects import AIProvider, SentAt
from app.usecases.chat.generate_content import (
    GenerateContentHandler,
    GenerateContentQuery,
)


@pytest.fixture
def mock_ai_service(mocker: Any) -> IAIService:
    service = mocker.Mock(spec=IAIService)
    service.generate_content = mocker.AsyncMock(return_value=Ok("Generated Content"))
    service.provider = AIProvider.GEMINI
    return service


@pytest.mark.asyncio
async def test_generate_content_with_explicit_prompt(
    uow: IUnitOfWork, mock_ai_service: IAIService
):
    """Test successful content generation with explicit prompt."""
    handler = GenerateContentHandler(mock_ai_service, uow)
    prompt = "Hello AI"

    # Setup active instruction
    instruction = SystemInstruction.create(
        AIProvider.GEMINI, "You are a bot", is_active=True
    ).unwrap()
    async with uow:
        await uow.GetRepository(SystemInstruction).save(instruction)
        await uow.commit()

    # Execute
    query = GenerateContentQuery(prompt=prompt)
    result = await handler.handle(query)

    assert not is_err(result)
    assert result.unwrap().content == "Generated Content"

    # Verify interactions
    mock_ai_service.generate_content.assert_called_once()  # type: ignore
    call_args = mock_ai_service.generate_content.call_args  # type: ignore
    assert call_args[0][0] == prompt
    assert len(call_args[0][1]) == 0
    assert call_args[1]["system_instruction"] == "You are a bot"

    # Verify messages saved (Only Model message should be saved)
    async with uow:
        messages = (
            await uow.GetRepository(ChatMessage).get_recent_history(10)
        ).unwrap()
        assert len(messages) == 1
        assert messages[0].role == ChatRole.MODEL


@pytest.mark.asyncio
async def test_generate_content_from_history(
    uow: IUnitOfWork, mock_ai_service: IAIService
):
    """Test content generation fetching prompt from history."""
    handler = GenerateContentHandler(mock_ai_service, uow)

    # Setup active instruction
    instruction = SystemInstruction.create(
        AIProvider.GEMINI, "You are a bot", is_active=True
    ).unwrap()

    # Save a user message first
    user_prompt = "Hello from DB"
    user_msg = ChatMessage.create(
        role=ChatRole.USER,
        content=user_prompt,
        sent_at=SentAt.from_primitive(datetime.now(UTC)).unwrap(),
    )

    async with uow:
        await uow.GetRepository(SystemInstruction).save(instruction)
        await uow.GetRepository(ChatMessage).add(user_msg)
        await uow.commit()

    # Execute without prompt
    query = GenerateContentQuery(prompt=None)
    result = await handler.handle(query)

    assert not is_err(result)
    assert result.unwrap().content == "Generated Content"

    # Verify interactions
    mock_ai_service.generate_content.assert_called_once()  # type: ignore
    call_args = mock_ai_service.generate_content.call_args  # type: ignore
    # The prompt passed to AI service should be the user message content
    assert call_args[0][0] == user_prompt
    # The history passed to AI service should be empty (since we popped the last message)
    assert len(call_args[0][1]) == 0

    # Verify messages saved (User + Model)
    async with uow:
        messages = (
            await uow.GetRepository(ChatMessage).get_recent_history(10)
        ).unwrap()
        assert len(messages) == 2
        assert messages[0].role == ChatRole.USER
        assert messages[1].role == ChatRole.MODEL


@pytest.mark.asyncio
async def test_generate_content_ai_failure(
    uow: IUnitOfWork, mock_ai_service: IAIService
):
    """Test AI service failure."""
    mock_ai_service.generate_content.return_value = Err("AI Error")  # type: ignore
    handler = GenerateContentHandler(mock_ai_service, uow)

    result = await handler.handle(GenerateContentQuery(prompt="Prompt"))

    assert is_err(result)
    assert "Failed to generate content" in result.error.message

    # Verify no messages saved (prompt was explicit, so nothing in DB)
    async with uow:
        messages = (
            await uow.GetRepository(ChatMessage).get_recent_history(10)
        ).unwrap()
        assert len(messages) == 0


@pytest.mark.asyncio
async def test_generate_content_history_failure(
    uow: IUnitOfWork, mock_ai_service: IAIService, mocker: Any
):
    """Test history retrieval failure."""
    mock_uow = mocker.Mock(spec=IUnitOfWork)
    mock_uow.__aenter__ = mocker.AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = mocker.AsyncMock(return_value=None)

    mock_repo = mocker.Mock()
    mock_repo.get_recent_history = mocker.AsyncMock(return_value=Err("DB Error"))

    mock_uow.GetRepository.return_value = mock_repo

    handler = GenerateContentHandler(mock_ai_service, mock_uow)

    result = await handler.handle(GenerateContentQuery(prompt="Prompt"))

    assert is_err(result)
    assert "Failed to retrieve chat history" in result.error.message
