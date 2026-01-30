from unittest.mock import AsyncMock, patch

import pytest

from app.core.result import Err, Ok
from app.domain.value_objects.session_id import SessionId
from app.infrastructure.services.shell_session_service import ShellSessionService


@pytest.mark.asyncio
async def test_start_session_success():
    """Test successful session start and gemini command execution."""
    service = ShellSessionService()
    session_id = SessionId.generate().unwrap()
    sid_str = session_id.to_primitive()

    # Mock process for screen creation
    mock_process_screen = AsyncMock()
    mock_process_screen.returncode = 0
    mock_process_screen.wait.return_value = None

    # Mock process for gemini command
    mock_process_gemini = AsyncMock()
    mock_process_gemini.returncode = 0
    mock_process_gemini.wait.return_value = None

    with patch(
        "asyncio.create_subprocess_exec",
        side_effect=[mock_process_screen, mock_process_gemini],
    ) as mock_exec:
        result = await service.start_session(session_id)

        assert isinstance(result, Ok)
        assert result.unwrap() is None

        # Verify calls
        assert mock_exec.call_count == 2

        # Check first call (screen creation)
        cmd1 = mock_exec.call_args_list[0][0]
        assert cmd1[0] == "screen"
        assert cmd1[1] == "-dmS"
        assert cmd1[2] == sid_str
        assert cmd1[3] == "bash"

        # Check second call (gemini command)
        cmd2 = mock_exec.call_args_list[1][0]
        assert cmd2[0] == "screen"
        assert cmd2[2] == sid_str
        assert cmd2[6] == "stuff"
        assert cmd2[7] == "gemini\n"


@pytest.mark.asyncio
async def test_start_session_screen_creation_failure():
    """Test failure during screen session creation."""
    service = ShellSessionService()
    session_id = SessionId.generate().unwrap()

    # Mock process for screen creation failure
    mock_process_screen = AsyncMock()
    mock_process_screen.returncode = 1
    mock_process_screen.wait.return_value = None
    mock_process_screen.communicate.return_value = (b"", b"screen error")

    with patch(
        "asyncio.create_subprocess_exec", side_effect=[mock_process_screen]
    ) as mock_exec:
        result = await service.start_session(session_id)

        assert isinstance(result, Err)
        assert "Screen failed with code 1" in str(result.error)

        # Should only be called once
        assert mock_exec.call_count == 1


@pytest.mark.asyncio
async def test_start_session_gemini_execution_failure():
    """Test failure during gemini command execution."""
    service = ShellSessionService()
    session_id = SessionId.generate().unwrap()

    # Mock process for screen creation success
    mock_process_screen = AsyncMock()
    mock_process_screen.returncode = 0
    mock_process_screen.wait.return_value = None

    # Mock process for gemini failure
    mock_process_gemini = AsyncMock()
    mock_process_gemini.returncode = 1
    mock_process_gemini.wait.return_value = None
    mock_process_gemini.communicate.return_value = (b"", b"gemini execution failed")

    with patch(
        "asyncio.create_subprocess_exec",
        side_effect=[mock_process_screen, mock_process_gemini],
    ) as mock_exec:
        result = await service.start_session(session_id)

        assert isinstance(result, Err)
        assert "Failed to start gemini in screen: 1" in str(result.error)

        # Should be called twice
        assert mock_exec.call_count == 2
