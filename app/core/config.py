from pathlib import Path

from dotenv import load_dotenv


def load_app_environment() -> None:
    """
    Load environment variables from .env files.
    Prioritizes .env.local over .env.
    """
    # config.py is in app/core/config.py
    # Project root is ../../
    root_dir = Path(__file__).resolve().parent.parent.parent

    # Load .env.local first (development override)
    env_local = root_dir / ".env.local"
    if env_local.exists():
        load_dotenv(env_local)

    # Load .env (production/default)
    env_file = root_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
