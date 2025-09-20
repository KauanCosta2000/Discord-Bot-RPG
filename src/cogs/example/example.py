import discord
from discord.ext import commands

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping_command(self, ctx):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latência: **{latency_ms}ms**")

    @discord.app_commands.command(name="ping", description="Slash command de ping")
    async def ping_slash(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latência: **{latency_ms}ms**")

async def setup(bot):
    await bot.add_cog(Example(bot))