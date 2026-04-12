import discord
from discord.ext import commands
from discord import app_commands
import random
import logging
from typing import Dict, Any
import json

from utils.dice_parser import DiceParser

logger = logging.getLogger(__name__)

class DMTools(commands.Cog):
    """Dungeon Master tools and commands"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Encounter tables by CR
        self.encounter_tables = {
            0.25: {
                'easy': ['goblin', 'kobold', 'giant rat'],
                'medium': ['orc', 'skeleton', 'zombie'],
                'hard': ['ogre', 'troll', 'bugbear']
            },
            0.5: {
                'easy': ['orc', 'skeleton', 'giant spider'],
                'medium': ['ogre', 'bugbear', 'ghoul'],
                'hard': ['troll', 'owlbear', 'minotaur']
            },
            1: {
                'easy': ['bugbear', 'ghoul', 'giant'],
                'medium': ['troll', 'owlbear', 'minotaur'],
                'hard': ['young dragon', 'giant', 'demon']
            },
            2: {
                'easy': ['troll', 'owlbear', 'minotaur'],
                'medium': ['young dragon', 'giant', 'demon'],
                'hard': ['adult dragon', 'vampire', 'lich']
            },
            3: {
                'easy': ['young dragon', 'giant', 'demon'],
                'medium': ['adult dragon', 'vampire', 'lich'],
                'hard': ['ancient dragon', 'archdevil', 'demigod']
            }
        }
        
        # Loot tables
        self.loot_tables = {
            'crude': {
                'gold': (1, 6),
                'items': ['dagger', 'shortbow', 'leather armor', 'torch', 'rope'],
                'magic': []
            },
            'common': {
                'gold': (10, 60),
                'items': ['longsword', 'chain mail', 'potion of healing', 'scroll'],
                'magic': ['+1 weapon', 'potion of healing', 'scroll of fireball']
            },
            'uncommon': {
                'gold': (100, 600),
                'items': ['plate armor', 'greatsword', 'wand'],
                'magic': ['+2 weapon', 'bag of holding', 'cloak of protection']
            },
            'rare': {
                'gold': (1000, 6000),
                'items': ['masterwork armor', 'artifact'],
                'magic': ['+3 weapon', 'staff of power', 'ring of invisibility']
            },
            'legendary': {
                'gold': (10000, 60000),
                'items': ['artifact', 'legendary weapon'],
                'magic': ['vorpal sword', 'staff of the magi', 'ring of wishes']
            }
        }
    
    def is_dm(self, user: discord.User, guild: discord.Guild) -> bool:
        """Check if user has DM permissions"""
        member = guild.get_member(user.id)
        return member and (member.guild_permissions.manage_messages or member.guild_permissions.administrator)
    
    @app_commands.command(name="encounter", description="Generate random encounter")
    @app_commands.describe(
        cr="Challenge rating",
        difficulty="Encounter difficulty",
        party_size="Number of party members"
    )
    @app_commands.choices(difficulty=[
        app_commands.Choice(name="Easy", value="easy"),
        app_commands.Choice(name="Medium", value="medium"),
        app_commands.Choice(name="Hard", value="hard"),
        app_commands.Choice(name="Deadly", value="deadly")
    ])
    async def encounter(
        self, 
        interaction: discord.Interaction,
        cr: float = 1.0,
        difficulty: str = "medium",
        party_size: int = 4
    ):
        """Generate random encounter based on CR and party level"""
        if not self.is_dm(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need to be a DM or have manage messages permission to use this!",
                ephemeral=True
            )
            return
        
        try:
            # Round CR to nearest valid value
            valid_crs = [0.25, 0.5, 1, 2, 3]
            cr = min(valid_crs, key=lambda x: abs(x - cr))
            
            # Get encounter table
            if cr not in self.encounter_tables:
                cr = 1
            
            encounter_table = self.encounter_tables[cr][difficulty]
            
            # Generate encounter
            num_enemies = max(1, int(party_size * random.uniform(0.5, 2.0)))
            enemies = [random.choice(encounter_table) for _ in range(num_enemies)]
            
            # Calculate difficulty
            total_xp = num_enemies * cr * 100
            
            embed = discord.Embed(
                title="⚔️ Random Encounter",
                description=f"**Difficulty:** {difficulty.title()}\n**CR:** {cr}\n**Party Size:** {party_size}",
                color=discord.Color.red()
            )
            
            # Count enemies
            enemy_counts = {}
            for enemy in enemies:
                enemy_counts[enemy] = enemy_counts.get(enemy, 0) + 1
            
            enemy_list = "\n".join([f"{count}x {enemy.title()}" for enemy, count in enemy_counts.items()])
            embed.add_field(name="Enemies", value=enemy_list, inline=False)
            
            embed.add_field(name="Total XP", value=f"{total_xp:,}", inline=True)
            embed.add_field(name="Per Player", value=f"{total_xp // party_size:,}", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error generating encounter: {e}")
            await interaction.response.send_message(
                "Error generating encounter. Please check your parameters.",
                ephemeral=True
            )
    
    @app_commands.command(name="loot", description="Generate random loot")
    @app_commands.describe(
        level="Party level or treasure level",
        count="Number of items to generate"
    )
    async def loot(
        self, 
        interaction: discord.Interaction,
        level: int = 1,
        count: int = 1
    ):
        """Generate random loot based on level"""
        if not self.is_dm(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need to be a DM or have manage messages permission to use this!",
                ephemeral=True
            )
            return
        
        try:
            # Determine loot tier
            if level <= 4:
                tier = 'crude'
            elif level <= 10:
                tier = 'common'
            elif level <= 16:
                tier = 'uncommon'
            elif level <= 20:
                tier = 'rare'
            else:
                tier = 'legendary'
            
            loot_table = self.loot_tables[tier]
            generated_loot = []
            
            for _ in range(count):
                # Generate gold
                gold = random.randint(*loot_table['gold'])
                
                # Generate items
                items = []
                if random.random() < 0.7:  # 70% chance for basic items
                    items.append(random.choice(loot_table['items']))
                
                # Generate magic items
                magic = []
                if loot_table['magic'] and random.random() < 0.3:  # 30% chance for magic
                    magic.append(random.choice(loot_table['magic']))
                
                generated_loot.append({
                    'gold': gold,
                    'items': items,
                    'magic': magic
                })
            
            embed = discord.Embed(
                title="💰 Generated Loot",
                description=f"**Tier:** {tier.title()}\n**Level:** {level}",
                color=discord.Color.gold()
            )
            
            total_gold = 0
            all_items = []
            all_magic = []
            
            for loot_item in generated_loot:
                total_gold += loot_item['gold']
                all_items.extend(loot_item['items'])
                all_magic.extend(loot_item['magic'])
            
            embed.add_field(name="Gold", value=f"{total_gold:,} gp", inline=False)
            
            if all_items:
                embed.add_field(name="Items", value="\n".join(all_items), inline=True)
            
            if all_magic:
                embed.add_field(name="Magic Items", value="\n".join(all_magic), inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error generating loot: {e}")
            await interaction.response.send_message(
                "Error generating loot. Please check your parameters.",
                ephemeral=True
            )
    
    @app_commands.command(name="npc", description="Generate random NPC")
    @app_commands.describe(
        race="NPC race",
        profession="NPC profession",
        attitude="NPC attitude"
    )
    async def npc(
        self, 
        interaction: discord.Interaction,
        race: str = None,
        profession: str = None,
        attitude: str = None
    ):
        """Generate random NPC"""
        if not self.is_dm(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need to be a DM or have manage messages permission to use this!",
                ephemeral=True
            )
            return
        
        # NPC generation tables
        races = ['human', 'elf', 'dwarf', 'halfling', 'gnome', 'half-orc', 'tiefling', 'dragonborn']
        professions = [
            'merchant', 'blacksmith', 'innkeeper', 'guard', 'thief', 'priest', 'wizard', 'bard',
            'farmer', 'noble', 'sailor', 'soldier', 'herbalist', 'alchemist', 'ranger', 'hunter'
        ]
        attitudes = ['friendly', 'neutral', 'hostile', 'suspicious', 'helpful', 'indifferent']
        
        generated_race = race or random.choice(races)
        generated_profession = profession or random.choice(professions)
        generated_attitude = attitude or random.choice(attitudes)
        
        # Generate stats
        stats = {
            'str': random.randint(8, 18),
            'dex': random.randint(8, 18),
            'con': random.randint(8, 18),
            'int': random.randint(8, 18),
            'wis': random.randint(8, 18),
            'cha': random.randint(8, 18)
        }
        
        # Generate personality traits
        traits = [
            'speaks in riddles', 'has a mysterious past', 'is always cheerful',
            'has a dark secret', 'is extremely paranoid', 'loves to gamble',
            'is obsessed with cleanliness', 'collects strange objects',
            'speaks with an accent', 'has a distinctive scar'
        ]
        
        trait = random.choice(traits)
        
        embed = discord.Embed(
            title="👤 Random NPC",
            description=f"A {generated_race} {generated_profession}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Attitude", value=generated_attitude.title(), inline=True)
        embed.add_field(name="Trait", value=trait, inline=True)
        
        # Ability scores
        ability_text = (
            f"**STR:** {stats['str']} **DEX:** {stats['dex']} **CON:** {stats['con']}\n"
            f"**INT:** {stats['int']} **WIS:** {stats['wis']} **CHA:** {stats['cha']}"
        )
        embed.add_field(name="Stats", value=ability_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dungeon", description="Generate random dungeon room")
    @app_commands.describe(
        size="Room size",
        type="Room type"
    )
    @app_commands.choices(size=[
        app_commands.Choice(name="Small", value="small"),
        app_commands.Choice(name="Medium", value="medium"),
        app_commands.Choice(name="Large", value="large")
    ])
    @app_commands.choices(type=[
        app_commands.Choice(name="Combat", value="combat"),
        app_commands.Choice(name="Puzzle", value="puzzle"),
        app_commands.Choice(name="Treasure", value="treasure"),
        app_commands.Choice(name="Trap", value="trap")
    ])
    async def dungeon(
        self, 
        interaction: discord.Interaction,
        size: str = "medium",
        type: str = "combat"
    ):
        """Generate random dungeon room"""
        if not self.is_dm(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need to be a DM or have manage messages permission to use this!",
                ephemeral=True
            )
            return
        
        # Room generation tables
        sizes = {
            'small': '10x10 feet',
            'medium': '20x20 feet',
            'large': '30x30 feet'
        }
        
        room_types = {
            'combat': {
                'descriptions': [
                    'A room with ancient pillars and scattered debris',
                    'A dark chamber with flickering torchlight',
                    'A circular room with a raised dais in the center'
                ],
                'features': ['pillars', 'altar', 'statues', 'weapon racks', 'bones']
            },
            'puzzle': {
                'descriptions': [
                    'A room with intricate runes on the walls',
                    'A chamber with mysterious symbols on the floor',
                    'A room with a complex mechanism on the far wall'
                ],
                'features': ['runes', 'symbols', 'mechanism', 'inscriptions', 'levers']
            },
            'treasure': {
                'descriptions': [
                    'A dusty room with chests and crates',
                    'A chamber with glittering objects on shelves',
                    'A room with ornate decorations and hidden compartments'
                ],
                'features': ['chests', 'crates', 'shelves', 'decorations', 'compartments']
            },
            'trap': {
                'descriptions': [
                    'A room with suspicious holes in the walls',
                    'A chamber with loose floor tiles',
                    'A room with strange markings on the floor'
                ],
                'features': ['holes', 'tiles', 'markings', 'pressure plates', 'tripwires']
            }
        }
        
        # Generate room
        room_desc = random.choice(room_types[type]['descriptions'])
        features = random.sample(room_types[type]['features'], 2)
        
        embed = discord.Embed(
            title=f"🏰 {type.title()} Room",
            description=room_desc,
            color=discord.Color.purple()
        )
        
        embed.add_field(name="Size", value=sizes[size], inline=True)
        embed.add_field(name="Features", value=", ".join(features), inline=True)
        
        # Add random elements
        if type == 'combat':
            enemies = random.randint(1, 4)
            embed.add_field(name="Enemies", value=f"{enemies} creatures", inline=True)
        elif type == 'treasure':
            value = random.randint(50, 500)
            embed.add_field(name="Treasure Value", value=f"{value} gp", inline=True)
        elif type == 'trap':
            dc = random.randint(10, 20)
            embed.add_field(name="Trap DC", value=str(dc), inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(DMTools(bot))