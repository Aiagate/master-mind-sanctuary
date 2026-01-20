from typing import Any

from app.core.config import load_app_environment


def test_load_app_environment_prioritizes_local(mocker: Any):
    mock_load_dotenv = mocker.patch("app.core.config.load_dotenv")
    mock_exists = mocker.patch("app.core.config.Path.exists")

    # Setup mock_exists to return True for both .env and .env.local
    mock_exists.return_value = True

    # Act
    load_app_environment()

    # Assert
    # Should be called for both .env.local and .env
    assert mock_load_dotenv.call_count == 2

    # Verify the order (it loads .env.local then .env)
    calls = mock_load_dotenv.call_args_list
    assert ".env.local" in str(calls[0][0][0])
    assert ".env" in str(calls[1][0][0])


def test_load_app_environment_skips_non_existent(mocker: Any):
    mock_load_dotenv = mocker.patch("app.core.config.load_dotenv")
    mock_exists = mocker.patch("app.core.config.Path.exists")

    # Setup mock_exists to return False
    mock_exists.return_value = False

    # Act
    load_app_environment()

    # Assert
    assert mock_load_dotenv.call_count == 0
