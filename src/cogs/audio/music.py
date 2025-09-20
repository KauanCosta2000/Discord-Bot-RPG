import discord
from discord.ext import commands
from discord import FFmpegOpusAudio, app_commands
import yt_dlp
# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
import logging
from typing import Optional

from config.config import Config

logger = logging.getLogger(__name__)

class Track:
    def __init__(self, title: str, url: str, duration: int, source: str, requester: discord.Member):
        self.title = title
        self.url = url
        self.duration = duration
        self.source = source
        self.requester = requester
    
    def __str__(self):
        return f"{self.title} ({self.source})"

class MusicQueue:
    def __init__(self):
        self.tracks = []
        self.loop = False
        self.shuffle = False
        self.current_index = 0
    
    def add(self, track: Track):
        self.tracks.append(track)
    
    def remove(self, index: int):
        if 0 <= index < len(self.tracks):
            return self.tracks.pop(index)
        return None
    
    def clear(self):
        self.tracks.clear()
        self.current_index = 0
    
    def next(self) -> Optional[Track]:
        if not self.tracks:
            return None
        
        if self.loop:
            self.current_index = (self.current_index + 1) % len(self.tracks)
        elif self.shuffle:
            import random
            self.current_index = random.randint(0, len(self.tracks) - 1)
        else:
            self.current_index += 1
            if self.current_index >= len(self.tracks):
                return None
        
        return self.tracks[self.current_index] if self.current_index < len(self.tracks) else None
    
    def previous(self) -> Optional[Track]:
        if not self.tracks:
            return None
        
        self.current_index = max(0, self.current_index - 1)
        return self.tracks[self.current_index]
    
    def current(self) -> Optional[Track]:
        if not self.tracks or self.current_index >= len(self.tracks):
            return None
        return self.tracks[self.current_index]
    
    def is_empty(self):
        return len(self.tracks) == 0

class GuildMusicState:
    def __init__(self):
        self.queue = MusicQueue()
        self.volume = Config.DEFAULT_VOLUME
        self.now_playing = None
        self.voice_client = None

class Music(commands.Cog):
    """Music and ambient sound commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.guild_states = {}
        
        # Initialize audio sources
        self.ytdl = yt_dlp.YoutubeDL({
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        })
        
        # Ambient sounds library
        self.ambient_sounds = {
            'tavern': [
                'https://www.youtube.com/watch?v=7w8vD7nw4IY',  # Medieval Tavern
                'https://www.youtube.com/watch?v=8q3hNo8q8eQ',  # Cozy Tavern
            ],
            'nature': [
                'https://www.youtube.com/watch?v=wzjWIxXBs_s',  # Forest Sounds
                'https://www.youtube.com/watch?v=ScgBvB_aM4g',  # Rain Sounds
            ],
            'battle': [
                'https://www.youtube.com/watch?v=7gKxD6Tsi2Y',  # Epic Battle Music
                'https://www.youtube.com/watch?v=9Wq4e2p7Q1Y',  # Boss Battle
            ],
            'exploration': [
                'https://www.youtube.com/watch?v=2O3D1cAF5bs',  # Adventure Music
                'https://www.youtube.com/watch?v=7gKxD6Tsi2Y',  # Exploration Theme
            ]
        }
    
    def get_guild_state(self, guild_id: int) -> GuildMusicState:
        """Get or create guild music state"""
        if guild_id not in self.guild_states:
            self.guild_states[guild_id] = GuildMusicState()
        return self.guild_states[guild_id]
    
    async def join_voice(self, interaction: discord.Interaction, channel: discord.VoiceChannel = None):
        """Join voice channel"""
        if channel is None:
            if interaction.user.voice and interaction.user.voice.channel:
                channel = interaction.user.voice.channel
            else:
                await interaction.response.send_message(
                    "You need to be in a voice channel or specify one!",
                    ephemeral=True
                )
                return False
        
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.voice_client and guild_state.voice_client.is_connected():
            await guild_state.voice_client.move_to(channel)
        else:
            guild_state.voice_client = await channel.connect()
        
        return True
    
    async def leave_voice(self, interaction: discord.Interaction):
        """Leave voice channel"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.voice_client and guild_state.voice_client.is_connected():
            await guild_state.voice_client.disconnect()
            guild_state.voice_client = None
            guild_state.queue.clear()
            await interaction.response.send_message("Left voice channel.")
        else:
            await interaction.response.send_message("Not in a voice channel!")
    
    async def play_track(self, interaction: discord.Interaction, track: Track):
        """Play a track"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if not guild_state.voice_client or not guild_state.voice_client.is_connected():
            if not await self.join_voice(interaction):
                return
        
        try:
            # Get audio source
            if track.source == 'youtube':
                audio_source = await self.get_youtube_audio(track.url, volume=guild_state.volume)
            else:
                await interaction.followup.send("Unsupported audio source!")
                return
            
            # Play audio
            guild_state.voice_client.play(
                audio_source,
                after=lambda e: self.bot.loop.create_task(self.play_next(interaction))
            )
            
            guild_state.now_playing = track
            
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{track.title}**\nRequested by: {track.requester.mention}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error playing track: {e}")
            await interaction.followup.send(f"Error playing track: {str(e)}")

    
    async def get_youtube_audio(self, url: str, volume: float = 1.0):
      """Get YouTube audio source with volume control"""
      try:
          info = self.ytdl.extract_info(url, download=False)
          url2 = info['formats'][0]['url']
          audio_source = FFmpegOpusAudio(
              info['url'],  # direto do yt_dlp
              executable=Config.FFMPEG_EXECUTABLE,
              options='-vn',
              before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
          )
          return audio_source
      except Exception as e:
          logger.error(f"Error extracting YouTube audio: {e}")
          raise
    
    async def play_next(self, interaction: discord.Interaction):
        """Play next track in queue"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.queue.is_empty():
            guild_state.now_playing = None
            return
        
        next_track = guild_state.queue.next()
        if next_track:
            await self.play_track(interaction, next_track)
    
    @app_commands.command(name="play", description="Play a song or add to queue")
    @app_commands.describe(query="Song name, URL, or search query")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play music from various sources"""
        await interaction.response.defer()
        
        # Determine source and get track info
        track = None
        
        if 'youtube.com' in query or 'youtu.be' in query:
            track = await self.create_youtube_track(query, interaction.user)
        else:
            track = await self.search_youtube(query, interaction.user)
        
        if not track:
            await interaction.followup.send("Could not find that track!")
            return
        
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.now_playing is None:
            await self.play_track(interaction, track)
        else:
            guild_state.queue.add(track)
            embed = discord.Embed(
                title="🎵 Added to Queue",
                description=f"**{track.title}**\nPosition: #{len(guild_state.queue.tracks)}",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
    
    async def create_youtube_track(self, url: str, requester: discord.Member) -> Track:
        """Create YouTube track object"""
        try:
            info = self.ytdl.extract_info(url, download=False)
            return Track(
                title=info['title'],
                url=url,
                duration=info.get('duration', 0),
                source='youtube',
                requester=requester
            )
        except Exception as e:
            logger.error(f"Error creating YouTube track: {e}")
            return None
    
    
    async def search_youtube(self, query: str, requester: discord.Member) -> Track:
        """Search YouTube and return first result"""
        try:
            info = self.ytdl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
                return Track(
                    title=entry['title'],
                    url=entry['webpage_url'],
                    duration=entry.get('duration', 0),
                    source='youtube',
                    requester=requester
                )
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
        return None
    
    @app_commands.command(name="pause", description="Pause the current track")
    async def pause(self, interaction: discord.Interaction):
        """Pause current track"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.voice_client and guild_state.voice_client.is_playing():
            guild_state.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused")
        else:
            await interaction.response.send_message("Nothing is playing!")
    
    @app_commands.command(name="resume", description="Resume the current track")
    async def resume(self, interaction: discord.Interaction):
        """Resume current track"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.voice_client and guild_state.voice_client.is_paused():
            guild_state.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed")
        else:
            await interaction.response.send_message("Nothing is paused!")
    
    @app_commands.command(name="skip", description="Skip to next track")
    async def skip(self, interaction: discord.Interaction):
        """Skip current track"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.voice_client and guild_state.voice_client.is_playing():
            guild_state.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped")
        else:
            await interaction.response.send_message("Nothing is playing!")
    
    @app_commands.command(name="stop", description="Stop playing and clear queue")
    async def stop(self, interaction: discord.Interaction):
        """Stop playing and clear queue"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.voice_client:
            guild_state.voice_client.stop()
            guild_state.queue.clear()
            guild_state.now_playing = None
            await interaction.response.send_message("⏹️ Stopped and cleared queue")
        else:
            await interaction.response.send_message("Not playing anything!")
    
    @app_commands.command(name="queue", description="Show the current queue")
    async def queue(self, interaction: discord.Interaction):
        """Show current queue"""
        guild_state = self.get_guild_state(interaction.guild_id)
        
        if guild_state.queue.is_empty():
            await interaction.response.send_message("Queue is empty!")
            return
        
        embed = discord.Embed(
            title="🎵 Current Queue",
            color=discord.Color.blue()
        )
        
        # Current track
        if guild_state.now_playing:
            embed.add_field(
                name="Now Playing",
                value=f"**{guild_state.now_playing.title}**\nRequested by: {guild_state.now_playing.requester.mention}",
                inline=False
            )
        
        # Queue tracks
        queue_text = ""
        for i, track in enumerate(guild_state.queue.tracks[:10], 1):
            queue_text += f"{i}. {track.title} - {track.requester.mention}\n"
        
        if len(guild_state.queue.tracks) > 10:
            queue_text += f"\n... and {len(guild_state.queue.tracks) - 10} more"
        
        if queue_text:
            embed.add_field(name="Queue", value=queue_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="volume", description="Set volume")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, interaction: discord.Interaction, volume: int):
        """Set volume level"""
        if not 0 <= volume <= 100:
            await interaction.response.send_message("Volume must be between 0 and 100!")
            return
        
        guild_state = self.get_guild_state(interaction.guild_id)
        guild_state.volume = volume / 100
        
        if guild_state.voice_client and guild_state.voice_client.source:
            guild_state.voice_client.source.volume = guild_state.volume
        
        await interaction.response.send_message(f"🔊 Volume set to {volume}%")
    
    @app_commands.command(name="loop", description="Toggle loop mode")
    async def loop(self, interaction: discord.Interaction):
        """Toggle loop mode"""
        guild_state = self.get_guild_state(interaction.guild_id)
        guild_state.queue.loop = not guild_state.queue.loop
        
        status = "enabled" if guild_state.queue.loop else "disabled"
        await interaction.response.send_message(f"🔁 Loop {status}")
    
    @app_commands.command(name="shuffle", description="Toggle shuffle mode")
    async def shuffle(self, interaction: discord.Interaction):
        """Toggle shuffle mode"""
        guild_state = self.get_guild_state(interaction.guild_id)
        guild_state.queue.shuffle = not guild_state.queue.shuffle
        
        status = "enabled" if guild_state.queue.shuffle else "disabled"
        await interaction.response.send_message(f"🔀 Shuffle {status}")
    
    @app_commands.command(name="ambient", description="Play ambient sounds")
    @app_commands.describe(type="Type of ambient sound")
    @app_commands.choices(type=[
        app_commands.Choice(name="Tavern", value="tavern"),
        app_commands.Choice(name="Nature", value="nature"),
        app_commands.Choice(name="Battle", value="battle"),
        app_commands.Choice(name="Exploration", value="exploration")
    ])
    async def ambient(self, interaction: discord.Interaction, type: str):
        """Play ambient background sounds"""
        if type not in self.ambient_sounds:
            await interaction.response.send_message("Invalid ambient sound type!")
            return
        
        urls = self.ambient_sounds[type]
        url = urls[0]  # Use first URL for now
        
        track = await self.create_youtube_track(url, interaction.user)
        if track:
            await self.play_track(interaction, track)

    @app_commands.command(name="leave", description="Leave voice channel")
    async def leave(self, interaction: discord.Interaction):
        """Leave voice channel"""
        await self.leave_voice(interaction)

async def setup(bot):
    await bot.add_cog(Music(bot))