from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog
from app.core.mediator import Mediator
from app.core.result import is_ok
from app.usecases.system_instructions.create_system_instruction import (
    CreateSystemInstructionCommand,
)


class SystemInstructionCog(BaseCog, name="SystemInstructions"):
    """システム指示(System Instruction)を管理するCog。"""

    @commands.group(name="sys", invoke_without_command=True)
    async def sys_group(self, ctx: commands.Context[commands.Bot]) -> None:
        """システム指示管理コマンド。"""
        if ctx.command:
            await ctx.send_help(ctx.command)

    @sys_group.command(name="create")
    async def create_instruction(
        self,
        ctx: commands.Context[commands.Bot],
        provider_str: str,
        *,
        instruction: str,
    ) -> None:
        """
        新しいシステム指示を作成します。

        使用法: !sys create <Provider> <Instruction Text>
        例: !sys create Gemini あなたは役に立つアシスタントです。
        """
        # デフォルトでは非アクティブで作成する
        command = CreateSystemInstructionCommand(
            provider=provider_str,
            instruction=instruction,
            is_active=False,
        )

        result = await Mediator.send_async(command)

        if is_ok(result):
            instruction_id = result.unwrap().id
            await ctx.send(f"システム指示を作成しました。ID: {instruction_id}")
        else:
            error = result.error
            await ctx.send(f"指示の作成に失敗しました: {error.message}")
