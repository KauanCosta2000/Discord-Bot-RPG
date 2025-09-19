# RPG Discord Bot

A comprehensive Discord bot for D&D 5e and RPG management with music, dice rolling, character sheets, and DM tools.

## Features

### 🎵 Music & Ambience
- Play music from YouTube, Spotify, and SoundCloud
- Queue management with loop and shuffle
- Volume controls and ambient sounds
- Playlist system for custom soundtracks

### 🎲 Dice Rolling & Probability
- Standard dice notation (1d20+5)
- Advantage/disadvantage rolls
- Hidden GM rolls
- Initiative tracker with turn order
- Character sheet integration

### 📚 D&D 5e Reference
- Complete spell lookup
- Monster stat blocks
- Class information
- Item descriptions
- Search functionality

### 🧙 Character Management
- Save character sheets with stats, HP, AC
- HP tracking with damage and healing
- Spell casting and slot management
- Inventory management
- Campaign notes storage

### 👑 DM Tools
- Random encounter generator
- Loot tables and treasure generation
- NPC generator
- Dungeon room generator
- Secret DM commands

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Discord Bot Token
- FFmpeg (for audio playback)

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd discord-rpg-bot
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create .env file:**
```bash
cp .env.example .env
```

5. **Edit .env file with your configuration:**
```
DISCORD_TOKEN=your_bot_token_here
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

6. **Install FFmpeg:**
- **Windows:** Download from https://ffmpeg.org/download.html
- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`

### Running the Bot

1. **Start the bot:**
```bash
python main.py
```

2. **The bot will automatically:**
- Create necessary database tables
- Sync slash commands
- Start listening for commands

## Usage

### Basic Commands

#### Music
- `/play <query>` - Play music (YouTube, Spotify, SoundCloud)
- `/pause` - Pause current track
- `/resume` - Resume current track
- `/queue` - Show current queue
- `/ambient <type>` - Play ambient sounds (tavern, nature, battle, exploration)

#### Dice Rolling
- `/roll 1d20+5` - Roll dice with modifier
- `/adv 1d20+3` - Roll with advantage
- `/dis 1d20+3` - Roll with disadvantage
- `/initiative <character>` - Roll initiative
- `/init-show` - Show initiative order

#### D&D Reference
- `/spell fireball` - Get spell information
- `/monster goblin` - Get monster stats
- `/class wizard` - Get class information
- `/item bag of holding` - Get item details
- `/search fire` - Search D&D content

#### Character Management
- `/character-create` - Create new character
- `/character-view` - View your character
- `/hp +10` - Heal 10 HP
- `/hp -5` - Take 5 damage
- `/inventory-add sword` - Add item to inventory
- `/cast fireball` - Cast a spell

#### DM Tools
- `/encounter 2 medium` - Generate CR 2 medium encounter
- `/loot 5 3` - Generate 3 loot items for level 5
- `/npc` - Generate random NPC
- `/dungeon combat` - Generate combat room

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Bot token from Discord Developer Portal | Required |
| `COMMAND_PREFIX` | Prefix for traditional commands | `/` |
| `OWNER_IDS` | Comma-separated list of owner Discord IDs | None |
| `SPOTIFY_CLIENT_ID` | Spotify API client ID | Optional |
| `SPOTIFY_CLIENT_SECRET` | Spotify API client secret | Optional |
| `DEFAULT_VOLUME` | Default music volume (0.0-1.0) | `0.5` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Permissions

The bot requires the following permissions:
- Send Messages
- Embed Links
- Read Message History
- Connect to Voice Channels
- Speak in Voice Channels
- Manage Messages (for DM commands)

## Development

### Adding New Commands

1. Create a new cog in `cogs/` directory
2. Add your commands using `@app_commands.command()`
3. Register the cog in `main.py`

### Database Schema

The bot uses SQLite for data storage with tables for:
- Characters (user_id, guild_id, name, class, level, hp, ac, etc.)
- Campaigns (guild_id, name, dm_id, notes)
- Playlists (guild_id, name, tracks, created_by)
- Initiative (guild_id, participants, current_turn)

## Troubleshooting

### Common Issues

**Bot not responding:**
- Check if the bot token is correct in .env
- Ensure the bot has necessary permissions
- Check console for error messages

**Music not playing:**
- Verify FFmpeg is installed and accessible
- Check if the bot has voice channel permissions
- Ensure the bot is in a voice channel

**Commands not appearing:**
- Try `/reload <cog_name>` if you're the owner
- Wait a few minutes for global command sync
- Check bot permissions in the server

### Support

For support, check:
1. Console logs for error messages
2. The bot.log file for detailed logs
3. Ensure all dependencies are installed
4. Verify environment variables are set correctly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.