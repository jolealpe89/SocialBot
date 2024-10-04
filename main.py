#import discord
#from discord.ext import commands
#import os
#import tracemalloc
#import asyncio
#
#
## Prefixo do seu bot (pode ser alterado conforme necessário)
#prefixo = ",s"
#
#
#class SocialBot(commands.Bot):
#    def __init__(self):
#        super().__init__(command_prefix=commands.when_mentioned_or(prefixo), intents=discord.Intents().all())
#
#
#
## Configurar o bot
#intents = discord.Intents.all()
#bot = commands.Bot(command_prefix=prefixo, intents=intents)
#bot.remove_command('help')
#
#
#async def load_cogs():
#    for filename in os.listdir('./cogs'):
#        if filename.endswith('.py'):
#            tracemalloc.start()
#            await bot.load_extension(f'cogs.{filename[:-3]}')
#
## Evento quando o bot está pronto
#@bot.event
#async def on_ready():
#    try:
#        synced = await bot.tree.sync()
#        print(f"Bot pronto como {len(synced)} comandos.")
#        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"/pinto"), status=discord.Status.dnd)
#
#    except Exception as e:
#        print(f"Ocorreu um erro: {e}")
#
#async def main():
#      
#    await load_cogs()
#
#if __name__ == "__main__":
#
#
#    asyncio.run(main())
#
## Executar o bot
#try:
#    with open("verde/token.txt", "r") as f:
#        token = f.read().strip()
#except FileNotFoundError:
#    print("Arquivo com o token não encontrado.")
#    token = ""
#
#    
#@bot.event
#async def on_command_error(ctx, error):
#    if isinstance(error, commands.CommandNotFound):
#        await ctx.reply(f"O comando `{ctx.invoked_with}` não existe. Digite `{prefixo}help` para ver a lista de comandos disponíveis.")
#bot.run(token)
#-------------------------------------------------------------------------------------
import discord
from discord.ext import commands
import os
import tracemalloc
import asyncio
from datetime import datetime

# Prefixo do seu bot (pode ser alterado conforme necessário)
prefixo = ",s"

# Caminho da pasta de logs
log_dir = "X9"
log_file = os.path.join(log_dir, "command_log.txt")

# Função para garantir que a estrutura de diretórios existe
def ensure_log_directory():
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

# Função para salvar informações em um arquivo de log
def log_command(ctx):
    ensure_log_directory()
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = f"{ctx.author} - {ctx.author.display_name} (ID: {ctx.author.id})"
        guild = f"{ctx.guild.name} (ID: {ctx.guild.id})" if ctx.guild else "Mensagem privada"
        channel = f"{ctx.channel.name} (ID: {ctx.channel.id})" if ctx.guild else "Mensagem privada"
        command = f"Comando: {ctx.command.name}"
        log_message = f"[{timestamp}] {user} usou {command} no canal {channel} do servidor {guild}\n"
        f.write(log_message)

class SocialBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(prefixo), intents=discord.Intents().all())

# Configurar o bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefixo, intents=intents)
bot.remove_command('help')

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            tracemalloc.start()
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Evento quando o bot está pronto
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Bot pronto com {len(synced)} comandos.")
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"/pinto"), status=discord.Status.dnd)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Evento para logar comandos usados
@bot.event
async def on_command(ctx):
    log_command(ctx)  # Chama a função para salvar o log do comando

async def main():
    await load_cogs()

if __name__ == "__main__":
    asyncio.run(main())

# Executar o bot
try:
    with open("verde/token.txt", "r") as f:
        token = f.read().strip()
except FileNotFoundError:
    print("Arquivo com o token não encontrado.")
    token = ""

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(f"O comando `{ctx.invoked_with}` não existe. Digite `{prefixo}help` para ver a lista de comandos disponíveis.")
bot.run(token)