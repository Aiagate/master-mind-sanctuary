import discord
from discord.ext import commands

from app.bot.cogs.base_cog import BaseCog


class SubscriptionCog(BaseCog, name="Subscription"):
    """購読に関連するコマンドを管理するCog。"""

    @commands.command(name="subscribe-ai")
    async def subscribe(self, ctx: commands.Context[commands.Bot]) -> None:
        """
        購読を開始し、ユーザーにDMを送信します。

        使用法: !subscribe
        """
        try:
            message = (
                "Master-Mind-Sanctuary へようこそ！\n"
                "購読ありがとうございます。これから最新の情報をお届けします。"
            )
            await ctx.author.send(message)
            await ctx.send(
                f"{ctx.author.mention} さん、DMを送りました。確認してください！"
            )
        except discord.Forbidden:
            await ctx.send(
                f"{ctx.author.mention} さん、DMを送れませんでした。設定でDMを許可しているか確認してください。"
            )
        except Exception as e:
            await ctx.send(f"エラーが発生しました: {e}")
