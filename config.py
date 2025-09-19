import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '/')
    OWNER_IDS = [int(id) for id in os.getenv('OWNER_IDS', '').split(',') if id]
    
    # Spotify
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    # Audio
    FFMPEG_EXECUTABLE = os.getenv('FFMPEG_EXECUTABLE', 'ffmpeg')
    DEFAULT_VOLUME = float(os.getenv('DEFAULT_VOLUME', 0.5))
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///rpg_bot.db')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Bot Settings
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')
    ACTIVITY_STATUS = "RPG Adventures"
    
    # Audio Sources
    YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="
    SPOTIFY_BASE_URL = "https://open.spotify.com/track/"
    SOUNDCLOUD_BASE_URL = "https://soundcloud.com/"
    
    # D&D 5e Wikidot
    WIKIDOT_BASE_URL = "https://5e.d20srd.org"
    UNOFFICIAL_WIKIDOT_URLS = {
        'tasha': "https://tashas-cauldron-of-everything.wikidot.com",
        'xanathar': "https://xanathars-guide-to-everything.wikidot.com",
        'multiverse': "https://monsters-of-the-multiverse.wikidot.com"
    }