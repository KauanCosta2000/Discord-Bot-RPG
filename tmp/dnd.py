import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio

from utils.dnd_data import dnd_data

logger = logging.getLogger(__name__)

class DnD(commands.Cog):
    """D&D 5e reference commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="spell", description="Look up a spell")
    @app_commands.describe(name="Name of the spell")
    async def spell(self, interaction: discord.Interaction, name: str):
        """Look up spell information"""
        await interaction.response.defer()
        
        try:
            async with dnd_data:
                spell_data = await dnd_data.get_spell(name)
            
            if not spell_data:
                # Try searching for similar spells
                async with dnd_data:
                    similar = await dnd_data.search_spells(name)
                
                if similar:
                    embed = discord.Embed(
                        title="🔍 Spell Not Found",
                        description=f"Spell '{name}' not found. Did you mean:",
                        color=discord.Color.orange()
                    )
                    embed.add_field(name="Similar Spells", value="\n".join(similar))
                else:
                    embed = discord.Embed(
                        title="❌ Spell Not Found",
                        description=f"Could not find spell '{name}'",
                        color=discord.Color.red()
                    )
                
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📜 {spell_data['name']}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Level", value=spell_data['level'], inline=True)
            embed.add_field(name="School", value=spell_data['school'], inline=True)
            embed.add_field(name="Casting Time", value=spell_data['casting_time'], inline=False)
            embed.add_field(name="Range", value=spell_data['range'], inline=True)
            embed.add_field(name="Components", value=spell_data['components'], inline=True)
            embed.add_field(name="Duration", value=spell_data['duration'], inline=True)
            embed.add_field(name="Description", value=spell_data['description'][:1024], inline=False)
            
            if spell_data['at_higher_levels']:
                embed.add_field(name="At Higher Levels", value=spell_data['at_higher_levels'][:1024], inline=False)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error looking up spell: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not fetch spell information",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="monster", description="Look up a monster")
    @app_commands.describe(name="Name of the monster")
    async def monster(self, interaction: discord.Interaction, name: str):
        """Look up monster stat block"""
        await interaction.response.defer()
        
        try:
            async with dnd_data:
                monster_data = await dnd_data.get_monster(name)
            
            if not monster_data:
                # Try searching for similar monsters
                async with dnd_data:
                    similar = await dnd_data.search_monsters(name)
                
                if similar:
                    embed = discord.Embed(
                        title="🔍 Monster Not Found",
                        description=f"Monster '{name}' not found. Did you mean:",
                        color=discord.Color.orange()
                    )
                    embed.add_field(name="Similar Monsters", value="\n".join(similar))
                else:
                    embed = discord.Embed(
                        title="❌ Monster Not Found",
                        description=f"Could not find monster '{name}'",
                        color=discord.Color.red()
                    )
                
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"👹 {monster_data['name']}",
                color=discord.Color.red()
            )
            
            embed.add_field(name="Armor Class", value=monster_data['ac'], inline=True)
            embed.add_field(name="Hit Points", value=monster_data['hp'], inline=True)
            embed.add_field(name="Speed", value=monster_data['speed'], inline=True)
            
            # Ability scores
            abilities = f"**STR:** {monster_data['str']} | **DEX:** {monster_data['dex']} | **CON:** {monster_data['con']}\n"
            abilities += f"**INT:** {monster_data['int']} | **WIS:** {monster_data['wis']} | **CHA:** {monster_data['cha']}"
            embed.add_field(name="Ability Scores", value=abilities, inline=False)
            
            if monster_data['skills']:
                embed.add_field(name="Skills", value=monster_data['skills'], inline=True)
            if monster_data['senses']:
                embed.add_field(name="Senses", value=monster_data['senses'], inline=True)
            if monster_data['languages']:
                embed.add_field(name="Languages", value=monster_data['languages'], inline=True)
            
            embed.add_field(name="Challenge", value=monster_data['challenge'], inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error looking up monster: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not fetch monster information",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="class", description="Look up a class")
    @app_commands.describe(name="Name of the class")
    async def class_info(self, interaction: discord.Interaction, name: str):
        """Look up class information"""
        await interaction.response.defer()
        
        try:
            async with dnd_data:
                class_data = await dnd_data.get_class(name)
            
            if not class_data:
                embed = discord.Embed(
                    title="❌ Class Not Found",
                    description=f"Could not find class '{name}'",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"⚔️ {class_data['name']}",
                color=discord.Color.purple()
            )
            
            embed.add_field(name="Hit Dice", value=class_data['hit_dice'], inline=True)
            embed.add_field(name="Primary Ability", value=class_data['primary_ability'], inline=True)
            embed.add_field(name="Saving Throws", value=class_data['saves'], inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error looking up class: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not fetch class information",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="item", description="Look up an item")
    @app_commands.describe(name="Name of the item")
    async def item(self, interaction: discord.Interaction, name: str):
        """Look up item information"""
        await interaction.response.defer()
        
        try:
            async with dnd_data:
                item_data = await dnd_data.get_item(name)
            
            if not item_data:
                embed = discord.Embed(
                    title="❌ Item Not Found",
                    description=f"Could not find item '{name}'",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"🎒 {item_data['name']}",
                description=item_data['description'][:2048],
                color=discord.Color.green()
            )
            
            if item_data['type']:
                embed.add_field(name="Type", value=item_data['type'], inline=True)
            if item_data['rarity']:
                embed.add_field(name="Rarity", value=item_data['rarity'], inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error looking up item: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not fetch item information",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="search", description="Search for D&D content")
    @app_commands.describe(query="Search query", type="Type of content")
    @app_commands.choices(type=[
        app_commands.Choice(name="Spell", value="spell"),
        app_commands.Choice(name="Monster", value="monster"),
        app_commands.Choice(name="Class", value="class"),
        app_commands.Choice(name="Item", value="item")
    ])
    async def search(self, interaction: discord.Interaction, query: str, type: str = None):
        """Search for D&D content"""
        await interaction.response.defer()
        
        try:
            results = []
            
            if type == "spell" or type is None:
                async with dnd_data:
                    spell_results = await dnd_data.search_spells(query)
                    results.extend([f"📜 {spell}" for spell in spell_results])
            
            if type == "monster" or type is None:
                async with dnd_data:
                    monster_results = await dnd_data.search_monsters(query)
                    results.extend([f"👹 {monster}" for monster in monster_results])
            
            if not results:
                embed = discord.Embed(
                    title="🔍 No Results",
                    description=f"No results found for '{query}'",
                    color=discord.Color.orange()
                )
            else:
                embed = discord.Embed(
                    title=f"🔍 Search Results for '{query}'",
                    description="\n".join(results[:10]),
                    color=discord.Color.blue()
                )
                
                if len(results) > 10:
                    embed.set_footer(text=f"Showing first 10 of {len(results)} results")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not perform search",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(DnD(bot))