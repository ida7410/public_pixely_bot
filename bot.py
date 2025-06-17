import asyncio

import discord
from discord.ext import commands
from config import *
import logging
from db.mongo import connect_db


# Ensure the logs directory exists
os.makedirs('logs', exist_ok=True)

# Logging setup
log_handler = logging.FileHandler('logs/discord.log', encoding='utf-8')
log_handler.setLevel(logging.DEBUG)
logging.basicConfig(handlers=[log_handler], level=logging.WARNING)

# Intents and bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

async def setup_extensions():
    for ext in extensions:
        try:
            await bot.load_extension(ext)
            print(f"Loaded extension: {ext}")
        except Exception as e:
            print(f"Failed to load extension {ext}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        await asyncio.wait_for(bot.tree.sync(), timeout=10.0)
        print("commands synced")
    except asyncio.TimeoutError:
        print("timeout while syncing")
    except Exception as e:
        print(f"error syncing: {e}")
    await bot.change_presence(activity=discord.CustomActivity(name="작동 중"))


async def main():
    connect_db()  # Connect to MongoDB before bot starts
    async with bot:
        await setup_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("bot manually stopped")