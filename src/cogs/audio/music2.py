import discord
from discord.ext import commands
import yt_dlp


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def search_youtube(self, query: str):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "tmp/%(title)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "default_search": "ytsearch",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                return info["entries"][0]
            return info

    @commands.command(name="play")
    async def play(self, ctx, *, query: str):

        vc = ctx.author.voice
        if not vc or not vc.channel:
            return await ctx.send("❌ Você precisa estar em um canal de voz.")

        if ctx.voice_client is None:
            await vc.channel.connect()

        try:
            info = self.search_youtube(query)
            url = info["url"]
        except Exception as e:
            return await ctx.send(f"❌ Erro ao buscar música: {e}")

        source = await discord.FFmpegOpusAudio(
            url,
            options="-vn",
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        )
        ctx.voice_client.play(source)
        await ctx.send(f"▶️ Tocando: **{info['title']}**")


async def setup(bot):
    await bot.add_cog(Music(bot))
