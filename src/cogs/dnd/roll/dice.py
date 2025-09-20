import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional

from cogs.dnd.roll.dice_parser import DiceParser, InitiativeTracker

logger = logging.getLogger(__name__)

class Dice(commands.Cog):
    """Dice rolling and probability commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.initiative_trackers = {}  # guild_id -> InitiativeTracker
    
    def get_initiative_tracker(self, guild_id: int) -> InitiativeTracker:
        """Get or create initiative tracker for guild"""
        if guild_id not in self.initiative_trackers:
            self.initiative_trackers[guild_id] = InitiativeTracker()
        return self.initiative_trackers[guild_id]
    
    @app_commands.command(name="roll", description="Roll dice using standard notation")
    @app_commands.describe(
        notation="Dice notation (e.g., 1d20, 2d6+3, 1d20+5)",
        hidden="Make this roll hidden (DM only)"
    )
    async def roll(self, interaction: discord.Interaction, notation: str, hidden: bool = False):
        """Roll dice using standard notation"""
        try:
            roll_result = DiceParser.roll(notation)
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description=f"**Notation:** {notation}",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Results",
                value=f"**Total:** {roll_result.total}\n**Rolls:** {', '.join(map(str, roll_result.results))}",
                inline=False
            )
            
            if roll_result.advantage:
                embed.add_field(name="Mode", value="Advantage", inline=True)
            elif roll_result.disadvantage:
                embed.add_field(name="Mode", value="Disadvantage", inline=True)
            
            if roll_result.exploded:
                embed.add_field(
                    name="Exploded Dice",
                    value=', '.join(map(str, roll_result.exploded)),
                    inline=False
                )
            
            if hidden and interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed)
                
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Notation",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="adv", description="Roll with advantage")
    @app_commands.describe(notation="Dice notation (e.g., 1d20+5)")
    async def advantage(self, interaction: discord.Interaction, notation: str):
        """Roll with advantage"""
        try:
            roll_result = DiceParser.roll(f"adv {notation}")
            
            embed = discord.Embed(
                title="🎲 Advantage Roll",
                description=f"**Notation:** {notation}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="Results",
                value=f"**Total:** {roll_result.total}\n**Rolls:** {', '.join(map(str, roll_result.results))}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Notation",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="dis", description="Roll with disadvantage")
    @app_commands.describe(notation="Dice notation (e.g., 1d20+5)")
    async def disadvantage(self, interaction: discord.Interaction, notation: str):
        """Roll with disadvantage"""
        try:
            roll_result = DiceParser.roll(f"dis {notation}")
            
            embed = discord.Embed(
                title="🎲 Disadvantage Roll",
                description=f"**Notation:** {notation}",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="Results",
                value=f"**Total:** {roll_result.total}\n**Rolls:** {', '.join(map(str, roll_result.results))}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Notation",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="gmroll", description="Roll dice hidden from players (DM only)")
    @app_commands.describe(notation="Dice notation")
    async def gmroll(self, interaction: discord.Interaction, notation: str):
        """Hidden roll for DMs"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "You need to be a DM or have manage messages permission to use this!",
                ephemeral=True
            )
            return
        
        try:
            roll_result = DiceParser.roll(notation)
            
            embed = discord.Embed(
                title="🎲 DM Roll",
                description=f"**Notation:** {notation}",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="Results",
                value=f"**Total:** {roll_result.total}\n**Rolls:** {', '.join(map(str, roll_result.results))}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            embed = discord.Embed(
                title="❌ Invalid Notation",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="initiative", description="Roll initiative")
    @app_commands.describe(
        character="Character name",
        modifier="Dexterity modifier",
        add_to_tracker="Add to initiative tracker"
    )
    async def initiative(self, interaction: discord.Interaction, character: str, modifier: int = 0, add_to_tracker: bool = True):
        """Roll initiative for a character"""
        try:
            init_result = DiceParser.initiative_roll(character, modifier)
            
            embed = discord.Embed(
                title="⚡ Initiative Roll",
                description=f"**{character}**",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="Roll",
                value=f"1d20 + {modifier} = **{init_result['total']}**",
                inline=False
            )
            
            if add_to_tracker:
                tracker = self.get_initiative_tracker(interaction.guild_id)
                tracker.add_participant(character, init_result['total'])
                
                embed.add_field(
                    name="Tracker",
                    value=f"{character} added to initiative tracker",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="init-add", description="Add participant to initiative tracker")
    @app_commands.describe(
        character="Character name",
        initiative="Initiative value",
        hp="Hit points (optional)",
        ac="Armor class (optional)"
    )
    async def init_add(self, interaction: discord.Interaction, character: str, initiative: int, hp: int = None, ac: int = None):
        """Add participant to initiative tracker"""
        tracker = self.get_initiative_tracker(interaction.guild_id)
        tracker.add_participant(character, initiative, hp, ac)
        
        embed = discord.Embed(
            title="⚡ Initiative Added",
            description=f"**{character}** (Initiative: {initiative})",
            color=discord.Color.green()
        )
        
        if hp:
            embed.add_field(name="HP", value=str(hp), inline=True)
        if ac:
            embed.add_field(name="AC", value=str(ac), inline=True)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="init-remove", description="Remove participant from initiative tracker")
    @app_commands.describe(character="Character name to remove")
    async def init_remove(self, interaction: discord.Interaction, character: str):
        """Remove participant from initiative tracker"""
        tracker = self.get_initiative_tracker(interaction.guild_id)
        tracker.remove_participant(character)
        
        embed = discord.Embed(
            title="⚡ Initiative Removed",
            description=f"**{character}** removed from initiative tracker",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="init-show", description="Show current initiative order")
    async def init_show(self, interaction: discord.Interaction):
        """Show current initiative order"""
        tracker = self.get_initiative_tracker(interaction.guild_id)
        
        if not tracker.participants:
            await interaction.response.send_message("No participants in initiative tracker!")
            return
        
        embed = discord.Embed(
            title="⚡ Initiative Order",
            description=f"Round {tracker.round_number}",
            color=discord.Color.gold()
        )
        
        current = tracker.get_current()
        
        order_text = ""
        for i, participant in enumerate(tracker.participants, 1):
            marker = "👉 " if participant == current else "   "
            status = f" (HP: {participant['hp']}, AC: {participant['ac']})" if participant['hp'] or participant['ac'] else ""
            order_text += f"{marker}{i}. **{participant['name']}** - {participant['initiative']}{status}\n"
        
        embed.add_field(name="Order", value=order_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="init-next", description="Move to next turn in initiative")
    async def init_next(self, interaction: discord.Interaction):
        """Move to next turn"""
        tracker = self.get_initiative_tracker(interaction.guild_id)
        
        if not tracker.participants:
            await interaction.response.send_message("No participants in initiative tracker!")
            return
        
        next_participant = tracker.next_turn()
        
        embed = discord.Embed(
            title="⚡ Next Turn",
            description=f"**{next_participant['name']}**'s turn\nRound {tracker.round_number}",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="init-reset", description="Reset initiative tracker")
    async def init_reset(self, interaction: discord.Interaction):
        """Reset initiative tracker"""
        tracker = self.get_initiative_tracker(interaction.guild_id)
        tracker.reset()
        
        embed = discord.Embed(
            title="⚡ Initiative Reset",
            description="Initiative tracker has been reset",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roll-stats", description="Roll standard D&D ability scores")
    async def roll_stats(self, interaction: discord.Interaction):
        """Roll 6 sets of 4d6 drop lowest for D&D stats"""
        stats = []
        rolls_text = ""
        
        for i in range(6):
            rolls = [random.randint(1, 6) for _ in range(4)]
            rolls.sort()
            stat = sum(rolls[1:])  # Drop lowest
            stats.append(stat)
            rolls_text += f"Stat {i+1}: {rolls} → **{stat}**\n"
        
        total = sum(stats)
        embed = discord.Embed(
            title="🎲 Ability Scores",
            description="4d6 drop lowest",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Results", value=rolls_text, inline=False)
        embed.add_field(name="Total", value=f"**{total}**", inline=True)
        embed.add_field(name="Average", value=f"**{total/6:.1f}**", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Dice(bot))