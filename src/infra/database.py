import sqlite3
import aiosqlite
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "rpg_bot.db"):
        self.db_path = db_path
    
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Characters table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    class TEXT,
                    level INTEGER DEFAULT 1,
                    hp INTEGER,
                    max_hp INTEGER,
                    ac INTEGER,
                    ability_scores TEXT,
                    spells TEXT,
                    inventory TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Campaigns table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    dm_id INTEGER NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Sessions table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    summary TEXT,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
                )
            ''')
            
            # Playlists table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    tracks TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initiative tracker
            await db.execute('''
                CREATE TABLE IF NOT EXISTS initiative (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    encounter_name TEXT,
                    participants TEXT NOT NULL,
                    current_turn INTEGER DEFAULT 0,
                    round_number INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def get_character(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get character for user in guild"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM characters WHERE user_id = ? AND guild_id = ?",
                (user_id, guild_id)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'user_id': row[1],
                        'guild_id': row[2],
                        'name': row[3],
                        'class': row[4],
                        'level': row[5],
                        'hp': row[6],
                        'max_hp': row[7],
                        'ac': row[8],
                        'ability_scores': json.loads(row[9]) if row[9] else {},
                        'spells': json.loads(row[10]) if row[10] else [],
                        'inventory': json.loads(row[11]) if row[11] else [],
                        'created_at': row[12],
                        'updated_at': row[13]
                    }
        return None
    
    async def save_character(self, user_id: int, guild_id: int, character_data: Dict[str, Any]):
        """Save or update character"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check if character exists
            existing = await self.get_character(user_id, guild_id)
            
            if existing:
                await db.execute('''
                    UPDATE characters 
                    SET name = ?, class = ?, level = ?, hp = ?, max_hp = ?, 
                        ac = ?, ability_scores = ?, spells = ?, inventory = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ? AND guild_id = ?
                ''', (
                    character_data.get('name'),
                    character_data.get('class'),
                    character_data.get('level', 1),
                    character_data.get('hp'),
                    character_data.get('max_hp'),
                    character_data.get('ac'),
                    json.dumps(character_data.get('ability_scores', {})),
                    json.dumps(character_data.get('spells', [])),
                    json.dumps(character_data.get('inventory', [])),
                    user_id, guild_id
                ))
            else:
                await db.execute('''
                    INSERT INTO characters 
                    (user_id, guild_id, name, class, level, hp, max_hp, ac, 
                     ability_scores, spells, inventory)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, guild_id,
                    character_data.get('name'),
                    character_data.get('class'),
                    character_data.get('level', 1),
                    character_data.get('hp'),
                    character_data.get('max_hp'),
                    character_data.get('ac'),
                    json.dumps(character_data.get('ability_scores', {})),
                    json.dumps(character_data.get('spells', [])),
                    json.dumps(character_data.get('inventory', []))
                ))
            await db.commit()
    
    async def get_campaign(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get campaign for guild"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM campaigns WHERE guild_id = ?",
                (guild_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'guild_id': row[1],
                        'name': row[2],
                        'dm_id': row[3],
                        'notes': row[4],
                        'created_at': row[5]
                    }
        return None
    
    async def create_campaign(self, guild_id: int, name: str, dm_id: int) -> int:
        """Create new campaign"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO campaigns (guild_id, name, dm_id) VALUES (?, ?, ?)",
                (guild_id, name, dm_id)
            )
            await db.commit()
            return cursor.lastrowid
    
    async def save_playlist(self, guild_id: int, name: str, tracks: list, created_by: int):
        """Save playlist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO playlists (guild_id, name, tracks, created_by)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, name, json.dumps(tracks), created_by))
            await db.commit()
    
    async def get_playlist(self, guild_id: int, name: str) -> Optional[Dict[str, Any]]:
        """Get playlist by name"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT * FROM playlists WHERE guild_id = ? AND name = ?",
                (guild_id, name)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'guild_id': row[1],
                        'name': row[2],
                        'tracks': json.loads(row[3]),
                        'created_by': row[4],
                        'created_at': row[5]
                    }
        return None

# Global database instance
db = Database()