import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from mathparse import mathparse
import json
from datetime import datetime
import random
import asyncio

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
jaimeId = int(os.getenv("JAIME_USER_ID"))
mudaeRol = "MudaeSubscribed"
mudaeSubId = 1408437418289528934
mudaeEditId = 1408437424107028552
mudaeChannelId = 1408380741334728704

# File to store the last claim message ID
CLAIM_MESSAGE_FILE = "last_claim_message.json"

# Function to see if the content has a ,
def hasComma(text):
    return ',' in text

# Function to load the last claim message ID from file
def load_claim_message_id():
    try:
        with open(CLAIM_MESSAGE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('message_id')
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# Function to save the last claim message ID to file
def save_claim_message_id(message_id):
    try:
        with open(CLAIM_MESSAGE_FILE, 'w') as f:
            json.dump({'message_id': message_id}, f)
    except Exception as e:
        print(f"Error saving claim message ID: {e}")

# Set up basic logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Scheduled task for mudae claim reset notification
@tasks.loop(hours=3)
async def mudae_claim_reset():
    channel = bot.get_channel(mudaeChannelId)

    last_message_id = load_claim_message_id()
    if last_message_id:
        last_message = await channel.fetch_message(last_message_id)
        await last_message.delete()

    message = await channel.send("<@&1408382042739183648> el claim del mudae ha sido reiniciado")
    save_claim_message_id(message.id)

@mudae_claim_reset.before_loop
async def before_mudae_claim_reset():
    await bot.wait_until_ready()

    now = datetime.now()
    current_hour = now.hour
    next_3h_mark = ((current_hour // 3) + 1) * 3

    if next_3h_mark >= 24:
        next_3h_mark = 0

    hours_to_wait = (next_3h_mark - current_hour - 1 + 24) % 24
    minutes_to_wait = 60 - now.minute + 4
    seconds_to_wait = 60 - now.second

    if seconds_to_wait == 60:
        seconds_to_wait = 0
        minutes_to_wait += 1

    if minutes_to_wait == 60:
        minutes_to_wait = 0
        hours_to_wait = (hours_to_wait + 1) % 24

    total_seconds = hours_to_wait * 3600 + minutes_to_wait * 60 + seconds_to_wait

    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print(f"Next 3-hour mark: {next_3h_mark:02d}:05:00")
    print(f"Waiting {hours_to_wait}h {minutes_to_wait}m {seconds_to_wait}s before starting mudae claim reset task")

    await asyncio.sleep(total_seconds)

# Scheduled task for bingbong playing every hour
@tasks.loop(hours=1)
async def bingbong_play():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            if len(channel.members) > 0:
                voice_client = await channel.connect()
                music_folder = "sounds/bingbong"
                music_files = sorted([f for f in os.listdir(music_folder) if f.endswith(".mp3")])
                selected_song = random.choices(music_files, weights=[99.99, 0.01], k=1)[0]

                while not voice_client.is_connected():
                    await asyncio.sleep(0.1)

                voice_client.play(discord.FFmpegPCMAudio(os.path.join(music_folder, selected_song)))

                while voice_client.is_playing():
                    await asyncio.sleep(0.1)

                await voice_client.disconnect()

@bingbong_play.before_loop
async def before_bingbong_play():
    await bot.wait_until_ready()
    now = datetime.now()
    minutes_to_wait = 59 - now.minute
    seconds_to_wait = 59 - now.second
    total_seconds = minutes_to_wait * 60 + seconds_to_wait

    print(f"Current time: {now.strftime('%H:%M:%S')}")
    print(f"Waiting {minutes_to_wait}m {seconds_to_wait}s before starting bingbong play task")
    await asyncio.sleep(total_seconds)

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

    if not mudae_claim_reset.is_running():
        mudae_claim_reset.start()
        print("Started mudae claim reset task")

    if not bingbong_play.is_running():
        bingbong_play.start()
        print("Started bingbong play task")

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

    else:
        if "jaime" in message.content.lower() or f"<@{jaimeId}>" in message.content or f"<@!{jaimeId}>" in message.content or message.author.id == jaimeId:
            await message.reply("<:uh:1391363166910283799>")

        if "eran intermedios" in message.content.lower():
            await message.add_reaction("<:eran_intermedios:1408413491555078305>")

        if "fernando" in message.content.lower() or "alonso" in message.content.lower() or "33" in message.content.lower() or "adrian newey" in message.content.lower():
            sticker = await bot.fetch_sticker(1408397918658105406)
            await message.reply(stickers=[sticker])
        else:
            try:
                if mathparse.parse(message.content) == 33:
                    sticker = await bot.fetch_sticker(1408397918658105406)
                    await message.reply(stickers=[sticker])
            except Exception as e:
                print(f"Error processing mathparse: {e}")

    if "Wished by" in message.content and hasComma(message.content):
        await message.channel.send(f":star: Wish de varias personas contanto hasta 10 :alarm_clock: para que lo pueda pillar un tercero :star:\n")
        await asyncio.sleep(10)
        await message.channel.send(f":japanese_goblin: 10 segs cumplidos puede pillarlo un tercero :japanese_goblin:")

    await bot.process_commands(message)

## Event for reacting to the mudae message
@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id == bot.user.id:
        return

    if payload.message_id == mudaeSubId:
        guild = bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)

        if user is user.bot:
            return

        emoji_str = str(payload.emoji)
        if emoji_str == "✔️":
            rol = discord.utils.get(guild.roles, name=mudaeRol)
            if rol:
                await user.add_roles(rol)
        elif emoji_str == "❌":
            rol = discord.utils.get(guild.roles, name=mudaeRol)
            if rol:
                await user.remove_roles(rol)

## Event for handling mudaeRol added or removed
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        rol_before = discord.utils.get(before.roles, name=mudaeRol)
        rol_after = discord.utils.get(after.roles, name=mudaeRol)

        if rol_before is None and rol_after is not None:
            channel = bot.get_channel(mudaeChannelId)
            message = await channel.fetch_message(mudaeEditId)
            await message.edit(content=f"> Actualmente hay **{len([member for member in after.guild.members if discord.utils.get(member.roles, name=mudaeRol)])}** usuarios con el rol.")

        elif rol_before is not None and rol_after is None:
            channel = bot.get_channel(mudaeChannelId)
            message = await channel.fetch_message(mudaeEditId)
            await message.edit(content=f"> Actualmente hay **{len([member for member in after.guild.members if discord.utils.get(member.roles, name=mudaeRol)])}** usuarios con el rol.")

# Handling command
## Command to get the help message
@bot.hybrid_command(name="ayuda", description="🆘 Muestra un mensaje de ayuda")
async def ayuda(ctx: commands.Context):
    help_message = f"""Ahora mismo no hago mucho, pero iré aprendiendo.

Hay 2 formas de interactuar conmigo:
1. **Comandos de barra**: Usa `/` seguido del comando.
2. **Comandos de prefijo**: Usa `!` seguido del comando.

Puedes usar los siguientes comandos:
- **ayuda**: Muestra este mensaje de ayuda.
- **saluda**: Saluda en general.
- **saluda @usuario**: Saluda a un usuario del servidor.
- **asigna**: Te asigna el rol *{mudaeRol}*.
- **quita**: Te quita el rol *{mudaeRol}*.
- **encuesta "pregunta"**: Crea una encuesta de sí o no con la pregunta proporcionada.
- **bingbong**: 🕰️ Bing Bong 🕰️

También tengo eventos que se activan automáticamente pero tendréis que descubrirlos."""
    await ctx.send(help_message)

## Command to greet a user or in general
@bot.hybrid_command(name="saluda", description="👋 Saluda a otro usuario del servidor o en general")
async def saluda(ctx: commands.Context, usuario: discord.Member = None):
    if usuario is None:
        message = f"👋 {ctx.author.mention} quiere saludar al servidor en general 👋"
    else:
        message = f"{ctx.author.mention} te quiere saludar solo a tí {usuario.mention} 🫵👋"

    await ctx.send(message)

## Command to assign the mudae role
@bot.hybrid_command(name="asigna", description=f"🔧 Te asigna el rol {mudaeRol}")
async def asigna(ctx):
    rol = discord.utils.get(ctx.guild.roles, name=mudaeRol)
    if rol:
        await ctx.author.add_roles(rol)
        await ctx.send(f"Rol **{mudaeRol}** asignado a {ctx.author.mention} 🕴️")
    else:
        await ctx.send(f"El rol **{mudaeRol}** no existe en este servidor 🕴️")

## Command to remove the mudae role
@bot.hybrid_command(name="quita", description=f"🔧 Te quita el rol {mudaeRol}")
async def quita(ctx):
    rol = discord.utils.get(ctx.guild.roles, name=mudaeRol)
    if rol:
        await ctx.author.remove_roles(rol)
        await ctx.send(f"Rol **{mudaeRol}** quitado a {ctx.author.mention} 🕴️")
    else:
        await ctx.send(f"El rol **{mudaeRol}** no existe en este servidor 🕴️")

## Command to make a poll
@bot.hybrid_command(name="encuesta", description="🗳️ Crea una encuesta")
async def encuesta(ctx: commands.Context, *, pregunta: str=None):
    if pregunta is not None:
        embed = discord.Embed(title="Encuesta", description=pregunta, color=discord.Color.yellow())
        message = await ctx.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")
    else:
        await ctx.send("Por favor, proporciona una pregunta para la encuesta 😡")

## Command to join the voice chat, play one of the .mp3 randomly and disconnect
@bot.hybrid_command(name="bingbong", description="🕰️ Bing Bong 🕰️")
async def bingbong(ctx: commands.Context):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        music_folder = "sounds/bingbong"
        music_files = sorted([f for f in os.listdir(music_folder) if f.endswith(".mp3")])
        selected_song = random.choices(music_files, weights=[99.99, 0.01], k=1)[0]

        while not voice_client.is_connected():
            await asyncio.sleep(0.1)

        voice_client.play(discord.FFmpegPCMAudio(os.path.join(music_folder, selected_song)))
        await ctx.send("🕰️ Bing Bong 🕰️")

        while voice_client.is_playing():
            await asyncio.sleep(0.1)

        await voice_client.disconnect()
    else:
        await ctx.send("🕰️ Bing Bong 🕰️")

# Run the bot
if __name__ == "__main__":
    if token:
        bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        exit(1)