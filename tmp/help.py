import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class Help(commands.Cog):
    """Help and information commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Show help information")
    @app_commands.describe(command="Specific command to get help for")
    async def help(self, interaction: discord.Interaction, command: str = None):
        """Show help information"""
        if command:
            # Show specific command help
            await self.show_command_help(interaction, command)
        else:
            # Show general help
            await self.show_general_help(interaction)
    
    async def show_general_help(self, interaction: discord.Interaction):
        """Show general help menu"""
        embed = discord.Embed(
            title="🎲 RPG Bot Help",
            description="A comprehensive Discord bot for D&D 5e and RPG management",
            color=discord.Color.blue()
        )
        
        # Music commands
        embed.add_field(
            name="🎵 Music Commands",
            value=(
                "`/play <query>` - Play music from YouTube/Spotify/SoundCloud\n"
                "`/pause` - Pause current track\n"
                "`/resume` - Resume current track\n"
                "`/skip` - Skip to next track\n"
                "`/queue` - Show current queue\n"
                "`/volume <0-100>` - Set volume level\n"
                "`/ambient <type>` - Play ambient sounds"
            ),
            inline=False
        )
        
        # Dice commands
        embed.add_field(
            name="🎲 Dice Commands",
            value=(
                "`/roll <notation>` - Roll dice (e.g., 1d20+5)\n"
                "`/adv <notation>` - Roll with advantage\n"
                "`/dis <notation>` - Roll with disadvantage\n"
                "`/initiative <character>` - Roll initiative\n"
                "`/roll-stats` - Roll 4d6 drop lowest for stats"
            ),
            inline=False
        )
        
        # D&D commands
        embed.add_field(
            name="📚 D&D Commands",
            value=(
                "`/spell <name>` - Look up spell information\n"
                "`/monster <name>` - Look up monster stats\n"
                "`/class <name>` - Look up class information\n"
                "`/item <name>` - Look up item information\n"
                "`/search <query>` - Search D&D content"
            ),
            inline=False
        )
        
        # Character commands
        embed.add_field(
            name="🧙 Character Commands",
            value=(
                "`/character-create` - Create a new character\n"
                "`/character-view` - View your character\n"
                "`/hp <amount>` - Modify character HP\n"
                "`/cast <spell>` - Cast a spell\n"
                "`/inventory-add <item>` - Add item to inventory\n"
                "`/inventory-remove <item>` - Remove item from inventory"
            ),
            inline=False
        )
        
        # DM commands
        embed.add_field(
            name="👑 DM Commands",
            value=(
                "`/encounter <cr> <difficulty>` - Generate random encounter\n"
                "`/loot <level>` - Generate random loot\n"
                "`/npc` - Generate random NPC\n"
                "`/dungeon` - Generate random dungeon room"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use /help <command> for specific command help")
        
        await interaction.response.send_message(embed=embed)
    
    async def show_command_help(self, interaction: discord.Interaction, command: str):
        """Show help for specific command"""
        command_help = {
            'play': {
                'description': 'Play music from various sources',
                'usage': '/play <query>',
                'examples': [
                    '/play Never Gonna Give You Up',
                    '/play https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    '/play https://open.spotify.com/track/4cOdK2YGLEy7Rx2A1rtMLz'
                ]
            },
            'roll': {
                'description': 'Roll dice using standard notation',
                'usage': '/roll <notation>',
                'examples': [
                    '/roll 1d20+5',
                    '/roll 2d6',
                    '/roll 1d20+3'
                ]
            },
            'spell': {
                'description': 'Look up spell information from D&D 5e',
                'usage': '/spell <spell name>',
                'examples': [
                    '/spell fireball',
                    '/spell cure wounds',
                    '/spell magic missile'
                ]
            }
        }
        
        if command.lower() in command_help:
            help_data = command_help[command.lower()]
            
            embed = discord.Embed(
                title=f"Help: {command}",
                description=help_data['description'],
                color=discord.Color.green()
            )
            
            embed.add_field(name="Usage", value=f"`{help_data['usage']}`", inline=False)
            
            if 'examples' in help_data:
                examples_text = "\n".join([f"• {example}" for example in help_data['examples']])
                embed.add_field(name="Examples", value=examples_text, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Command Not Found",
                description=f"Could not find help for `{command}`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="about", description="Show bot information")
    async def about(self, interaction: discord.Interaction):
        """Show bot information"""
        embed = discord.Embed(
            title="🎲 About RPG Bot",
            description="A comprehensive Discord bot for D&D 5e and RPG management",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Features",
            value=(
                "• 🎵 Music player with YouTube/Spotify/SoundCloud support\n"
                "• 🎲 Advanced dice rolling with initiative tracker\n"
                "• 📚 Complete D&D 5e SRD reference\n"
                "• 🧙 Character and campaign management\n"
                "• 👑 DM tools for encounters and loot\n"
                "• 🌐 Multi-language support"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Usage",
            value="Use `/help` to see all available commands",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ for the RPG community")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))