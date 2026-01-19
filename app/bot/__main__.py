import logging
import os
import sys

import discord
from discord.ext import commands
from injector import Injector

from app.core.config import load_app_environment


class MyBot(commands.Bot):
    def __init__(self, command_prefix: str = "/") -> None:
        super().__init__(
            intents=discord.Intents.all(),
            command_prefix=command_prefix,
        )
        self.injector: Injector | None = None

    async def setup_hook(self) -> None:
        self.injector = await self._setup_dependencies()

        # Initialize AI Agent (Caching etc.)
        from app.domain.interfaces.ai_service import IAIService

        ai_service = self.injector.get(IAIService)
        await ai_service.initialize_ai_agent()

        self.bg_tasks = set()

        # Initialize Event Bus
        from app.bot.cogs.brain_cog import BrainCog
        from app.bot.cogs.chat_cog import ChatCog
        from app.bot.cogs.dm_response_cog import DirectMessageResponseCog
        from app.bot.cogs.embedding_cog import EmbeddingCog
        from app.bot.cogs.subscription_cog import SubscriptionCog
        from app.bot.cogs.system_instruction_cog import SystemInstructionCog
        from app.domain.interfaces.event_bus import IEventBus

        event_bus = self.injector.get(IEventBus)

        # Start Event Bus task
        t_bus = self.loop.create_task(event_bus.start())
        self.bg_tasks.add(t_bus)
        t_bus.add_done_callback(self.bg_tasks.discard)

        # Load Cogs with EventBus
        await self.add_cog(BrainCog(self, event_bus))
        await self.add_cog(ChatCog(self, event_bus))
        await self.add_cog(DirectMessageResponseCog(self, event_bus))
        await self.add_cog(SubscriptionCog(self))
        await self.add_cog(SystemInstructionCog(self))
        await self.add_cog(EmbeddingCog(self))

    async def _setup_dependencies(self) -> "Injector":
        """Initialize database and dependencies."""

        from app import container
        from app.core.mediator import Mediator
        from app.infrastructure.database import init_db

        db_url = os.getenv("DATABASE_URL")
        if db_url is None:
            raise ValueError("DATABASE_URL environment variable is not set")

        init_db(db_url, echo=True)

        # Initialize Mediator with dependency injection container
        injector = Injector([container.configure])
        Mediator.initialize(injector)

        return injector


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            "[ %(levelname)-8s] %(asctime)s | %(name)-16s %(funcName)-16s| %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 環境変数を読み込む
    load_app_environment()

    # Bot トークンを取得
    token = os.getenv("DISCORD_BOT_TOKEN")
    if token is None:
        logging.error("DISCORD_BOT_TOKEN environment variable is not set")
        logging.error("Please set it in .env.local or .env file")
        sys.exit(1)

    bot = MyBot()
    bot.run(token)


if __name__ == "__main__":
    main()
