import discord
from discord.ext import commands
from discord import app_commands
import logging
from config import Config

logger = logging.getLogger(__name__)

class Admin(commands.Cog):
    """Admin and utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency}ms**",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stats", description="Show bot statistics")
    async def stats(self, interaction: discord.Interaction):
        """Show bot statistics"""
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Commands", value=str(len(self.bot.tree.get_commands())), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reload", description="Reload a cog (Owner only)")
    @app_commands.describe(cog="Name of the cog to reload")
    async def reload(self, interaction: discord.Interaction, cog: str):
        """Reload a cog"""
        if interaction.user.id not in Config.OWNER_IDS:
            await interaction.response.send_message(
                "You don't have permission to use this command!",
                ephemeral=True
            )
            return
        
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = discord.Embed(
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded `{cog}`",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to reload `{cog}`: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="shutdown", description="Shutdown the bot (Owner only)")
    async def shutdown(self, interaction: discord.Interaction):
        """Shutdown the bot"""
        if interaction.user.id not in Config.OWNER_IDS:
            await interaction.response.send_message(
                "You don't have permission to use this command!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🛑 Shutting Down",
            description="Bot is shutting down...",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))