from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog
from app.core.mediator import Mediator
from app.core.result import is_ok
from app.domain.interfaces.ai_service import IEmbeddingService
from app.usecases.embeddings.get_embedding import GetEmbeddingQuery


class EmbeddingCog(BaseCog, name="Embedding"):
    """Embedding生成機能のテスト用Cog。"""

    @commands.group(name="embedding", invoke_without_command=True)
    async def embedding_group(self, ctx: commands.Context[commands.Bot]) -> None:
        """Embedding機能テストコマンド。"""
        if ctx.command:
            await ctx.send_help(ctx.command)

    @embedding_group.command(name="test")
    async def test(self, ctx: commands.Context[commands.Bot], *, text: str) -> None:
        """
        指定されたテキストのEmbeddingを生成してテストします。

        使用法: !embedding test <Text>
        例: !embedding test こんにちは
        """
        query = GetEmbeddingQuery(text=text)
        result = await Mediator.send_async(query)

        if is_ok(result):
            value = result.unwrap()
            embedding = value.embedding
            length = len(embedding)
            preview = embedding[:5]

            provider = "Unknown"
            injector = getattr(self.bot, "injector", None)
            if injector:
                try:
                    # IEmbeddingServiceがバインドされているか確認
                    service = injector.get(IEmbeddingService)
                    provider = str(service.provider)
                except Exception:
                    pass

            await ctx.send(
                f"Embedding生成成功!\n- 次元数: {length}\n- 先頭5要素: {preview}\n- Provider: {provider}"
            )
        else:
            error = result.error
            await ctx.send(f"Embedding生成失敗: {error.message}")
