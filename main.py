import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Load Opus audio codec (required for voice)
if not discord.opus.is_loaded():
    for lib in ("libopus.so.0", "libopus.so", "opus"):
        try:
            discord.opus.load_opus(lib)
            break
        except Exception:
            continue
    else:
        print("WARNING: Could not load Opus. Install it with: apt install libopus0")

PREFIX = "$$"


def make_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True

    bot = commands.Bot(command_prefix=PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} online")

    @bot.command(name="join")
    async def join(ctx):
        if not ctx.author.voice:
            return await ctx.reply("Join a VC first")
        await ctx.author.voice.channel.connect()
        await ctx.reply("Joined VC")

    @bot.command(name="leave")
    async def leave(ctx):
        if not ctx.voice_client:
            return await ctx.reply("Not in VC")
        await ctx.voice_client.disconnect()
        await ctx.reply("Left VC")

    @bot.command(name="play")
    async def play(ctx, song: str = None):
        if not song:
            return await ctx.reply("Example: $$play gugu")
        file = f"./{song}.mp3"
        if not os.path.isfile(file):
            return await ctx.reply(f"{song}.mp3 not found")
        if not ctx.voice_client:
            return await ctx.reply("Use $$join first")
        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(discord.FFmpegPCMAudio(file))
        await ctx.reply(f"Playing {song}")

    @bot.command(name="pause")
    async def pause(ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.reply("Paused")
        else:
            await ctx.reply("Nothing is playing")

    @bot.command(name="resume")
    async def resume(ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.reply("Resumed")
        else:
            await ctx.reply("Nothing is paused")

    @bot.command(name="stop")
    async def stop(ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.reply("Stopped")
        else:
            await ctx.reply("Not in VC")

    return bot


async def main():
    # Collect all TOKEN1, TOKEN2, TOKEN3... from .env
    tokens = []
    i = 1
    while True:
        token = os.getenv(f"TOKEN{i}")
        if not token:
            break
        tokens.append((i, token))
        i += 1

    if not tokens:
        print("No tokens found. Add TOKEN1, TOKEN2, ... to your .env file")
        return

    print(f"Starting {len(tokens)} bot(s)...")

    # Start all bots concurrently
    await asyncio.gather(
        *[run_bot(num, token) for num, token in tokens]
    )


async def run_bot(num, token):
    bot = make_bot()
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print(f"Bot {num}: Invalid token, skipping")
    except Exception as e:
        print(f"Bot {num}: Error — {e}")


asyncio.run(main())
