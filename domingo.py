import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
import sys

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
domingoChannelId = int(os.getenv("DOMINGO_CHANNEL_ID"))

# Set up basic logging to console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)


# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)


# Handling events
## Event when the bot is ready
@bot.event
async def on_ready():
    logging.info("Sending Domingo:")

    try:
        channel = bot.get_channel(domingoChannelId)
        if channel is None:
            channel = await bot.fetch_channel(domingoChannelId)

        domingo = discord.File("images/domingo.png")
        await channel.send(file=domingo)

        logging.info("Domingo Sent Succesfully")

    except Exception as e:
        logging.error(f"Domingo couldn't be sent: {e}")
    finally:
        await bot.close()


# Run the bot
if __name__ == "__main__":
    if token:
        bot.run(token)
    else:
        logging.critical("Error: DISCORD_TOKEN not found in environment variables.")
        exit(1)
