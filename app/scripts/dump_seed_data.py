import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

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

T = TypeVar("T", bound=SQLModel)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


async def fetch_all[T: SQLModel](session: Any, model_class: type[T]) -> list[T]:
    """Fetch all records for a given model."""
    statement = select(model_class)
    result = await session.execute(statement)
    return list(result.scalars().all())


def save_json(data: list[dict[str, Any]], filename: str):
    """Save data to a JSON file."""
    file_path = SEEDS_DIR / filename

    # Ensure directory exists
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"Writing {len(data)} records to {file_path}")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DateTimeEncoder)


async def dump_data():
    """Export database data to JSON files."""
    logger.info("Starting data dump to JSON files...")

    load_app_environment()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL is not set.")
        return

    init_db(database_url)

    async for session in get_session():
        # Dump System Instructions
        system_instructions = await fetch_all(session, SystemInstructionORM)
        system_instructions_data = [item.model_dump() for item in system_instructions]
        save_json(system_instructions_data, "system_instructions.json")

        # Dump Chat Messages
        chat_messages = await fetch_all(session, ChatMessageORM)
        chat_messages_data = [item.model_dump() for item in chat_messages]
        save_json(chat_messages_data, "chat_messages.json")

    logger.info("Data dump completed.")
    await get_engine().dispose()


def main():
    asyncio.run(dump_data())


if __name__ == "__main__":
    main()
