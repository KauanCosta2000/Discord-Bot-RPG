import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DnDData:
    """D&D 5e data fetcher from various sources"""
    
    def __init__(self):
        self.base_url = "https://5e.d20srd.org"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """Get spell information"""
        try:
            url = f"{self.base_url}/srd/spells/{spell_name.lower().replace(' ', '')}.htm"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse spell information
                spell_data = {
                    'name': spell_name.title(),
                    'level': '',
                    'casting_time': '',
                    'range': '',
                    'components': '',
                    'duration': '',
                    'school': '',
                    'description': '',
                    'at_higher_levels': ''
                }
                
                # Extract spell details from the page
                content = soup.find('div', class_='content')
                if content:
                    text = content.get_text(strip=True, separator='\n')
                    lines = text.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if 'Level:' in line:
                            spell_data['level'] = line.replace('Level:', '').strip()
                        elif 'Casting Time:' in line:
                            spell_data['casting_time'] = line.replace('Casting Time:', '').strip()
                        elif 'Range:' in line:
                            spell_data['range'] = line.replace('Range:', '').strip()
                        elif 'Components:' in line:
                            spell_data['components'] = line.replace('Components:', '').strip()
                        elif 'Duration:' in line:
                            spell_data['duration'] = line.replace('Duration:', '').strip()
                        elif 'School:' in line:
                            spell_data['school'] = line.replace('School:', '').strip()
                        elif 'Description:' in line:
                            # Find the description section
                            desc_start = text.find('Description:')
                            if desc_start != -1:
                                spell_data['description'] = text[desc_start + 12:].strip()[:500] + '...'
                
                return spell_data
                
        except Exception as e:
            logger.error(f"Error fetching spell {spell_name}: {e}")
            return None
    
    async def get_monster(self, monster_name: str) -> Optional[Dict[str, Any]]:
        """Get monster stat block"""
        try:
            url = f"{self.base_url}/srd/monsters/{monster_name.lower().replace(' ', '')}.htm"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Parse monster information
                monster_data = {
                    'name': monster_name.title(),
                    'size': '',
                    'type': '',
                    'alignment': '',
                    'ac': '',
                    'hp': '',
                    'speed': '',
                    'str': 0,
                    'dex': 0,
                    'con': 0,
                    'int': 0,
                    'wis': 0,
                    'cha': 0,
                    'skills': '',
                    'senses': '',
                    'languages': '',
                    'challenge': '',
                    'actions': [],
                    'special_abilities': []
                }
                
                content = soup.find('div', class_='content')
                if content:
                    text = content.get_text(strip=True, separator='\n')
                    
                    # Extract basic stats
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('Armor Class'):
                            monster_data['ac'] = line.replace('Armor Class', '').strip()
                        elif line.startswith('Hit Points'):
                            monster_data['hp'] = line.replace('Hit Points', '').strip()
                        elif line.startswith('Speed'):
                            monster_data['speed'] = line.replace('Speed', '').strip()
                        elif line.startswith('STR'):
                            # Parse ability scores
                            ability_line = line
                            abilities = ability_line.split()
                            if len(abilities) >= 6:
                                monster_data['str'] = int(abilities[1])
                                monster_data['dex'] = int(abilities[3])
                                monster_data['con'] = int(abilities[5])
                        elif line.startswith('INT'):
                            abilities = line.split()
                            if len(abilities) >= 6:
                                monster_data['int'] = int(abilities[1])
                                monster_data['wis'] = int(abilities[3])
                                monster_data['cha'] = int(abilities[5])
                
                return monster_data
                
        except Exception as e:
            logger.error(f"Error fetching monster {monster_name}: {e}")
            return None
    
    async def get_class(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get class information"""
        try:
            url = f"{self.base_url}/srd/classes/{class_name.lower()}.htm"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                class_data = {
                    'name': class_name.title(),
                    'hit_dice': '',
                    'primary_ability': '',
                    'saves': '',
                    'features': [],
                    'subclasses': []
                }
                
                content = soup.find('div', class_='content')
                if content:
                    text = content.get_text(strip=True, separator='\n')
                    
                    # Extract basic class info
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 'Hit Dice:' in line:
                            class_data['hit_dice'] = line.replace('Hit Dice:', '').strip()
                        elif 'Primary Ability:' in line:
                            class_data['primary_ability'] = line.replace('Primary Ability:', '').strip()
                        elif 'Saves:' in line:
                            class_data['saves'] = line.replace('Saves:', '').strip()
                
                return class_data
                
        except Exception as e:
            logger.error(f"Error fetching class {class_name}: {e}")
            return None
    
    async def get_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get item information"""
        try:
            # Try magic items first
            url = f"{self.base_url}/srd/magicitems/{item_name.lower().replace(' ', '')}.htm"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    # Try equipment
                    url = f"{self.base_url}/srd/equipment/{item_name.lower().replace(' ', '')}.htm"
                    async with self.session.get(url) as response2:
                        if response2.status != 200:
                            return None
                        response = response2
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                item_data = {
                    'name': item_name.title(),
                    'type': '',
                    'rarity': '',
                    'description': '',
                    'properties': []
                }
                
                content = soup.find('div', class_='content')
                if content:
                    text = content.get_text(strip=True, separator='\n')
                    item_data['description'] = text[:1000] + '...' if len(text) > 1000 else text
                
                return item_data
                
        except Exception as e:
            logger.error(f"Error fetching item {item_name}: {e}")
            return None
    
    async def search_spells(self, query: str) -> list:
        """Search for spells by partial name"""
        # This would ideally use a proper search API
        # For now, return common spells that match
        common_spells = [
            'fireball', 'magic missile', 'cure wounds', 'shield', 'mage armor',
            'lightning bolt', 'haste', 'slow', 'invisibility', 'fly',
            'counterspell', 'dispel magic', 'revivify', 'teleport', 'wish'
        ]
        
        matches = [spell for spell in common_spells if query.lower() in spell]
        return matches[:5]  # Return top 5 matches
    
    async def search_monsters(self, query: str) -> list:
        """Search for monsters by partial name"""
        common_monsters = [
            'goblin', 'orc', 'dragon', 'beholder', 'mind flayer',
            'troll', 'ogre', 'giant', 'demon', 'devil',
            'zombie', 'skeleton', 'vampire', 'werewolf', 'giant spider'
        ]
        
        matches = [monster for monster in common_monsters if query.lower() in monster]
        return matches[:5]

# Global instance
dnd_data = DnDData()