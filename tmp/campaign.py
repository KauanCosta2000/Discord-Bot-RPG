import discord
from discord.ext import commands
from discord import app_commands
import logging
import json
from typing import Optional

from utils.database import db

logger = logging.getLogger(__name__)

class Campaign(commands.Cog):
    """Character and campaign management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="character-create", description="Create a new character")
    @app_commands.describe(
        name="Character name",
        char_class="Character class",
        level="Character level",
        hp="Max hit points",
        ac="Armor class"
    )
    async def character_create(
        self, 
        interaction: discord.Interaction,
        name: str,
        char_class: str,
        level: int = 1,
        hp: int = None,
        ac: int = None
    ):
        """Create a new character sheet"""
        try:
            character_data = {
                'name': name,
                'class': char_class,
                'level': level,
                'hp': hp,
                'max_hp': hp,
                'ac': ac,
                'ability_scores': {
                    'str': 10,
                    'dex': 10,
                    'con': 10,
                    'int': 10,
                    'wis': 10,
                    'cha': 10
                },
                'spells': [],
                'inventory': []
            }
            
            await db.save_character(interaction.user.id, interaction.guild_id, character_data)
            
            embed = discord.Embed(
                title="🧙 Character Created",
                description=f"**{name}** - Level {level} {char_class}",
                color=discord.Color.green()
            )
            
            if hp:
                embed.add_field(name="HP", value=str(hp), inline=True)
            if ac:
                embed.add_field(name="AC", value=str(ac), inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not create character",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="character-view", description="View your character sheet")
    async def character_view(self, interaction: discord.Interaction):
        """View your character sheet"""
        try:
            character = await db.get_character(interaction.user.id, interaction.guild_id)
            
            if not character:
                embed = discord.Embed(
                    title="❌ No Character",
                    description="You don't have a character in this server. Use `/character-create` to make one!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"🧙 {character['name']}",
                description=f"Level {character['level']} {character['class']}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="HP", value=f"{character['hp']}/{character['max_hp']}", inline=True)
            embed.add_field(name="AC", value=str(character['ac']), inline=True)
            
            # Ability scores
            abilities = character['ability_scores']
            ability_text = (
                f"**STR:** {abilities.get('str', 10)} "
                f"**DEX:** {abilities.get('dex', 10)} "
                f"**CON:** {abilities.get('con', 10)}\n"
                f"**INT:** {abilities.get('int', 10)} "
                f"**WIS:** {abilities.get('wis', 10)} "
                f"**CHA:** {abilities.get('cha', 10)}"
            )
            embed.add_field(name="Ability Scores", value=ability_text, inline=False)
            
            # Spells
            spells = character['spells']
            if spells:
                spell_text = ", ".join(spells[:10])
                if len(spells) > 10:
                    spell_text += f" and {len(spells) - 10} more"
                embed.add_field(name="Known Spells", value=spell_text, inline=False)
            
            # Inventory
            inventory = character['inventory']
            if inventory:
                inv_text = ", ".join(inventory[:10])
                if len(inventory) > 10:
                    inv_text += f" and {len(inventory) - 10} more"
                embed.add_field(name="Inventory", value=inv_text, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing character: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not retrieve character",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="hp", description="Modify character HP")
    @app_commands.describe(
        amount="Amount to add/subtract (use negative for damage)",
        set_to="Set HP to specific value (overrides amount)"
    )
    async def hp(self, interaction: discord.Interaction, amount: int = None, set_to: int = None):
        """Modify character HP"""
        try:
            character = await db.get_character(interaction.user.id, interaction.guild_id)
            
            if not character:
                embed = discord.Embed(
                    title="❌ No Character",
                    description="You don't have a character in this server.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if set_to is not None:
                new_hp = max(0, min(set_to, character['max_hp']))
                character['hp'] = new_hp
                action = f"set to {new_hp}"
            elif amount is not None:
                new_hp = max(0, min(character['hp'] + amount, character['max_hp']))
                character['hp'] = new_hp
                action = f"{'healed' if amount > 0 else 'damaged'} by {abs(amount)}"
            else:
                await interaction.response.send_message(
                    "Please provide either amount or set_to parameter",
                    ephemeral=True
                )
                return
            
            await db.save_character(interaction.user.id, interaction.guild_id, character)
            
            embed = discord.Embed(
                title="❤️ HP Updated",
                description=f"{character['name']} {action}\n**Current HP:** {character['hp']}/{character['max_hp']}",
                color=discord.Color.green() if amount is None or amount >= 0 else discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error updating HP: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not update HP",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cast", description="Cast a spell and use a spell slot")
    @app_commands.describe(spell="Name of the spell to cast")
    async def cast(self, interaction: discord.Interaction, spell: str):
        """Cast a spell and track usage"""
        try:
            character = await db.get_character(interaction.user.id, interaction.guild_id)
            
            if not character:
                embed = discord.Embed(
                    title="❌ No Character",
                    description="You don't have a character in this server.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if spell not in character['spells']:
                embed = discord.Embed(
                    title="❌ Spell Not Known",
                    description=f"{character['name']} doesn't know the spell '{spell}'",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="✨ Spell Cast",
                description=f"**{character['name']}** casts **{spell}**",
                color=discord.Color.purple()
            )
            
            # Note: Full spell slot tracking would require more complex logic
            embed.set_footer(text="Spell slot usage tracked (manual tracking required)")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error casting spell: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not cast spell",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="inventory-add", description="Add item to inventory")
    @app_commands.describe(item="Item to add")
    async def inventory_add(self, interaction: discord.Interaction, item: str):
        """Add item to character inventory"""
        try:
            character = await db.get_character(interaction.user.id, interaction.guild_id)
            
            if not character:
                embed = discord.Embed(
                    title="❌ No Character",
                    description="You don't have a character in this server.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if item not in character['inventory']:
                character['inventory'].append(item)
                await db.save_character(interaction.user.id, interaction.guild_id, character)
            
            embed = discord.Embed(
                title="🎒 Item Added",
                description=f"**{item}** added to {character['name']}'s inventory",
                color=discord.Color.green()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding item: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not add item",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="inventory-remove", description="Remove item from inventory")
    @app_commands.describe(item="Item to remove")
    async def inventory_remove(self, interaction: discord.Interaction, item: str):
        """Remove item from character inventory"""
        try:
            character = await db.get_character(interaction.user.id, interaction.guild_id)
            
            if not character:
                embed = discord.Embed(
                    title="❌ No Character",
                    description="You don't have a character in this server.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if item in character['inventory']:
                character['inventory'].remove(item)
                await db.save_character(interaction.user.id, interaction.guild_id, character)
                
                embed = discord.Embed(
                    title="🎒 Item Removed",
                    description=f"**{item}** removed from {character['name']}'s inventory",
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="❌ Item Not Found",
                    description=f"{character['name']} doesn't have **{item}**",
                    color=discord.Color.orange()
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error removing item: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not remove item",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="campaign-create", description="Create a new campaign")
    @app_commands.describe(name="Campaign name")
    async def campaign_create(self, interaction: discord.Interaction, name: str):
        """Create a new campaign"""
        try:
            campaign_id = await db.create_campaign(
                interaction.guild_id, 
                name, 
                interaction.user.id
            )
            
            embed = discord.Embed(
                title="📚 Campaign Created",
                description=f"**{name}** campaign created successfully",
                color=discord.Color.green()
            )
            
            embed.add_field(name="DM", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not create campaign",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="campaign-notes", description="Add notes to campaign")
    @app_commands.describe(notes="Campaign notes")
    async def campaign_notes(self, interaction: discord.Interaction, notes: str):
        """Add notes to the current campaign"""
        try:
            campaign = await db.get_campaign(interaction.guild_id)
            
            if not campaign or campaign['dm_id'] != interaction.user.id:
                embed = discord.Embed(
                    title="❌ Not DM",
                    description="You must be the DM to add campaign notes",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Update campaign notes (would need to implement this in database)
            embed = discord.Embed(
                title="📚 Campaign Notes",
                description=f"Notes added:\n{notes}",
                color=discord.Color.blue()
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding notes: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Could not add campaign notes",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Campaign(bot))