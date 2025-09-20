import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config.config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class RPGBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guild_messages = True
        intents.guild_reactions = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            activity=discord.Game(name=Config.ACTIVITY_STATUS),
            status=discord.Status.online,
            help_command=None
        )
        
        self.config = Config
        self.initial_extensions = [
            'cogs.audio.music',
            'cogs.dice',
            'cogs.dnd',
            'cogs.campaign',
            'cogs.dm_tools',
            'cogs.admin',
            'cogs.help',
            'cogs.example.example'
        ]
    
    async def setup_hook(self):
        """Load all cogs when bot starts"""
        # Initialize database
        try:
            await db.initialize()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
        
        # Load extensions
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Argument",
                description=f"Missing required argument: `{error.param.name}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid Argument",
                description=str(error),
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)
        
        else:
            logger.error(f"Error in command {ctx.command}: {error}")
            embed = discord.Embed(
                title="❌ An Error Occurred",
                description="An unexpected error occurred. Please try again later.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, delete_after=10)

async def main():
    """Main bot runner"""
    bot = RPGBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())