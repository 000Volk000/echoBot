import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")

# Set up basic logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Handling events
## Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Estamos ready para funcionar, {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

## Event when a new member joins
@bot.event
async def on_member_join(member):
    await member.send(f"Bienvenido al *{member.guild.name}*, {member.name}, ponte cómodo aunque no demasiado.")

## Event when a message is sent
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "hola" in message.content.lower():
        await message.delete()
        await message.channel.send(f"¿De que vas {message.author.mention}?, aquí el unico que saluda soy yo.\n\nSi quieres saludar a alguien, usa el comando `/saluda`")

    if "jaime" in message.content.lower() or f"<@{390909965038125059}>" in message.content or f"<@!{390909965038125059}>" in message.content:
        await message.reply("<:uh:1391363166910283799>")

    await bot.process_commands(message)

# Handling commands
## Command to greet a user or in general
@bot.hybrid_command(name="saluda", description="👋 Saluda a otro usuario del servidor o en general")
async def saluda(ctx: commands.Context, usuario: discord.Member = None):
    if usuario is None:
        message = f"{ctx.author.mention} quiere saludar en general"
    else:
        message = f"{ctx.author.mention} te quiere saludar {usuario.mention}"

    await ctx.send(message)

# Run the bot
if __name__ == "__main__":
    if token:
        bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        exit(1)