import os
from typing import Any

import injector
import pytest

from app.container import AIModule
from app.domain.interfaces.ai_service import IAIService
from app.infrastructure.services.gemini_service import GeminiService
from app.infrastructure.services.gpt_service import GptService
from app.infrastructure.services.mock_ai_service import MockAIService


@pytest.fixture
def container():
    return injector.Injector([AIModule()])


def test_ai_provider_default_is_mock(mocker: Any):
    """Test that the default AI provider is MockAIService."""
    mocker.patch.dict(os.environ, {}, clear=True)
    container = injector.Injector([AIModule()])
    ai_service = container.get(IAIService)
    assert isinstance(ai_service, MockAIService)


def test_ai_provider_gemini(mocker: Any):
    """Test that setting AI_PROVIDER to 'gemini' uses GeminiService."""
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "gemini"})
    container = injector.Injector([AIModule()])
    ai_service = container.get(IAIService)
    assert isinstance(ai_service, GeminiService)


def test_ai_provider_gpt(mocker: Any):
    """Test that setting AI_PROVIDER to 'gpt' uses GptService."""
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "gpt"})
    container = injector.Injector([AIModule()])
    ai_service = container.get(IAIService)
    assert isinstance(ai_service, GptService)


def test_ai_provider_openai(mocker: Any):
    """Test that setting AI_PROVIDER to 'openai' uses GptService."""
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "openai"})
    container = injector.Injector([AIModule()])
    ai_service = container.get(IAIService)
    assert isinstance(ai_service, GptService)


def test_ai_provider_unknown_defaults_to_mock(mocker: Any):
    """Test that an unknown AI_PROVIDER defaults to MockAIService."""
    mocker.patch.dict(os.environ, {"AI_PROVIDER": "unknown_provider"})
    container = injector.Injector([AIModule()])
    ai_service = container.get(IAIService)
    assert isinstance(ai_service, MockAIService)
