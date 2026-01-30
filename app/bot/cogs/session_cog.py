"""Session Cog."""

from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog
from app.core.mediator import Mediator
from app.core.result import is_err
from app.usecases.session.create_session import CreateSessionCommand


class SessionCog(BaseCog, name="Session"):
    """Cog for session management."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize cog."""
        self.bot = bot

    @commands.hybrid_group(name="session")
    async def create_session(self, ctx: commands.Context[commands.Bot]) -> None:
        """Create a new shell session."""
        await ctx.defer(ephemeral=True)

        try:
            result = await Mediator.send_async(CreateSessionCommand())

            if is_err(result):
                await ctx.send(
                    f"Failed to create session: {result.error}", ephemeral=True
                )
                return

            session_id = result.unwrap()
            await ctx.send(
                f"Session created successfully! ID: {session_id}", ephemeral=True
            )
        except Exception as e:
            await ctx.send(f"An unexpected error occurred: {e}", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    """Setup function for cog loading."""
    await bot.add_cog(SessionCog(bot))
