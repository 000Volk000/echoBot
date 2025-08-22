import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
from mathparse import mathparse

# Load environment variables
load_dotenv()
token = os.getenv("DISCORD_TOKEN")
jaimeId = os.getenv("JAIME_USER_ID")
mudaeRol = "MudaeSubscribed"

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

    else:
        if "jaime" in message.content.lower() or f"<@{jaimeId}>" in message.content or f"<@!{jaimeId}>" in message.content or message.author.id == jaimeId:
            await message.reply("<:uh:1391363166910283799>")

        if "fernando" in message.content.lower() or "alonso" in message.content.lower() or "33" in message.content.lower() or "adrian newey" in message.content.lower() or mathparse.parse(message.content,language='SPA') == 33:
            sticker = await bot.fetch_sticker(1408397918658105406)
            await message.reply(stickers=[sticker])

    await bot.process_commands(message)

# Handling commands
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

# Run the bot
if __name__ == "__main__":
    if token:
        bot.run(token, log_handler=handler, log_level=logging.DEBUG)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        exit(1)