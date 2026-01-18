import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add the project root to the python path to allow imports from app
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sqlmodel import SQLModel, select

from app.core.config import load_app_environment
from app.infrastructure.database import get_engine, get_session, init_db
from app.infrastructure.orm_models.chat_message_orm import ChatMessageORM
from app.infrastructure.orm_models.system_instruction_orm import SystemInstructionORM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEEDS_DIR = Path(__file__).resolve().parent / "seeds"


def load_json_data(file_name: str) -> list[dict[str, Any]]:
    """Load data from a JSON file in the seeds directory."""
    file_path = SEEDS_DIR / file_name
    if not file_path.exists():
        logger.warning(f"Seed file not found: {file_path}")
        return []
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def parse_datetime(dt_str: Any) -> Any:
    """Parse datetime string from SQL dump format."""
    if not isinstance(dt_str, str):
        return dt_str
    try:
        # PostgreSQL dump format: '2026-01-04 13:46:59+00'
        # Remove +00 and parse
        clean_str = dt_str.split("+")[0]
        return datetime.fromisoformat(clean_str)
    except ValueError:
        return dt_str


async def seed_table(
    session: Any, model_class: type[SQLModel], data: list[dict[str, Any]]
):
    """Seed a specific table with data, avoiding duplicates by ID."""
    for item in data:
        # Convert datetime strings
        processed_item = {k: parse_datetime(v) for k, v in item.items()}

        # Check if exists
        statement = select(model_class).where(model_class.id == processed_item["id"])  # pyright: ignore [reportAttributeAccessIssue]
        result = await session.execute(statement)
        existing = result.scalar_one_or_none()

        if existing:
            logger.debug(
                f"{model_class.__name__} with id {processed_item['id']} already exists. Skipping."
            )
        else:
            logger.info(
                f"Creating {model_class.__name__} with id {processed_item['id']}."
            )
            obj = model_class(**processed_item)
            session.add(obj)


async def seed_data():
    """Import initial data into the database from JSON files."""
    logger.info("Starting data seeding from JSON files...")

    # Load environment variables
    load_app_environment()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL is not set.")
        return

    # Initialize database
    init_db(database_url)

    # Load data from JSON
    system_instructions_data = load_json_data("system_instructions.json")
    chat_messages_data = load_json_data("chat_messages.json")

    async for session in get_session():
        # Seed System Instructions
        if system_instructions_data:
            await seed_table(session, SystemInstructionORM, system_instructions_data)

        # Seed Chat Messages
        if chat_messages_data:
            await seed_table(session, ChatMessageORM, chat_messages_data)

        await session.commit()

    logger.info("Data seeding completed.")

    # Dispose the engine to close connection pool and allow script to exit
    await get_engine().dispose()


def main():
    asyncio.run(seed_data())


if __name__ == "__main__":
    main()
