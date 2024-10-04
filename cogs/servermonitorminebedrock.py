from discord.ext import commands, tasks
import psutil
import os
import requests
import subprocess
from mcrcon import MCRcon
import socket
import re
import discord

#PIPPI ENTROU DIA 21/07/2023
class ServerMineMonitorPocket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_process = None
        self.server_status = None
        self.server_status_channel_ids = self.load_channel_ids()
        self.server_status_channels = None
        self.log_file_path = r"E:\MINECRAFT_BEDROCK\logue.txt"
        self.server_port = 19132
        self.server_DNS = 'kawaiidesu.zapto.org'
        self.last_line_num = 0
        self.bot = bot
        self.status = False    

    def load_channel_ids(self):
        channel_ids = []
        try:
            with open("MinecraftPocket/canais.txt", "r", encoding='utf-8') as file:
                channel_ids = [int(line.strip()) for line in file.readlines()]
        except FileNotFoundError:
            print("Arquivo de canais não encontrado.")
        except Exception as e:
            print(f"Erro ao carregar IDs de canais: {e}")
        return channel_ids

    async def send_embed_to_channels(self, embed):
        if not self.server_status_channels:
            self.server_status_channels = [self.bot.get_channel(channel_id) for channel_id in self.server_status_channel_ids]

        for channel in self.server_status_channels:
            await channel.send(embed=embed)    


    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.clear_log_file()  # Limpar o arquivo de log antes de iniciar a leitura
        except Exception as e:
            print(f"Ocorreu um erro ao limpar o arquivo de log: {e}")
    
        await self.check_log.start()

    @tasks.loop(seconds=1)
    async def check_log(self):
        if not os.path.exists(self.log_file_path):
            return

        with open(self.log_file_path, "r", encoding='utf-8') as file:
            lines = file.readlines()

        new_lines = lines[self.last_line_num:]
        self.last_line_num = len(lines)
        servername = "`<SOCIAL HUB MINECRAFT SERVER>`:"

        for line in new_lines:
            if "Server started" in line:
                ip = await self.get_external_ip()
                role_id=1274800678073798676
                embed = discord.Embed(title=servername, description=f"Servidor ligado! ✅\nAdicione **{self.server_DNS}** e Porta {self.server_port} na lista de servidores.\n<@&{role_id}>", color=0x00FF00)
                embed.set_thumbnail(url='https://media1.tenor.com/m/y76xw2cQA3kAAAAC/welcome-door-open.gif')
                await self.send_embed_to_channels(embed)
            elif "Server stop" in line:
                embed = discord.Embed(title=servername, description="Servidor desligado! 🛑", color=0xFF0000)
                embed.set_thumbnail(url='https://media.tenor.com/89i-s0uzMMwAAAAi/corona-closed.gif')
                await self.send_embed_to_channels(embed)
            else:
                # Verificar se um jogador entrou no servidor
                match_login = re.match(r".*\[.* INFO\] Player connected: (.+), xuid: (\d+)", line)
                if match_login:
                    player_name = match_login.group(1)
                    xuid = match_login.group(2)
                    embed = discord.Embed(title=servername, description=f"**{player_name}** entrou no servidor!", color=0x00FF00)
                    embed.set_thumbnail(url='https://gifdb.com/images/high/hello-cute-cat-box-kns8e4qa95ne2tnv.gif')
                    embed.set_image(url=f'https://tlauncher.org/skin.php?username_catalog=nickname&username_file=tlauncher_{player_name}.png&mode=0&update=0')
                    await self.send_embed_to_channels(embed)

                # Verificar se um jogador desconectou do servidor
                match_logout = re.match(r".*\[.* INFO\] Player disconnected: (.+), xuid: (\d+), pfid: ([a-f0-9]+)", line)
                if match_logout:
                    player_name = match_logout.group(1)
                    xuid = match_logout.group(2)
                    pfid = match_logout.group(3)
                    embed = discord.Embed(title=servername, description=f"**{player_name}** saiu do servidor!", color=0xFF0000)
                    embed.set_thumbnail(url='https://banter.so/wp-content/uploads/2022/06/jakebye.gif')
                    embed.set_image(url=f'https://tlauncher.org/skin.php?username_catalog=nickname&username_file=tlauncher_{player_name}.png&mode=1&update=0')
                    await self.send_embed_to_channels(embed)


    def clear_log_file(self):
        with open(self.log_file_path, "w", encoding='utf-8') as file:
            file.truncate(0)

    async def send_message(self, message):
        if not self.server_status_channels:
            self.server_status_channels = self.bot.get_channel(self.server_status_channel_ids)
        await self.server_status_channels.send(message)

    async def get_external_ip(self):
        try:
            response = requests.get('https://api.ipify.org')
            return response.text
        except requests.RequestException:
            return 'Não foi possível obter o IP externo.'


    @commands.hybrid_command(with_app_command=True, help='Adiciona o canal atual na lista de alertas do Minecraft.')
    async def alertaminebedrock(self, ctx: commands.Context):

        if ctx.channel.id not in self.server_status_channel_ids:
            self.server_status_channel_ids.add(ctx.channel.id)
            with open('MinecraftPocket/canais.txt', 'a', encoding='utf-8') as f:
                f.write(str(ctx.channel.id) + '\n')

        await ctx.send('Servidor e canal adicionados aos monitorados.')


    @commands.hybrid_command(with_app_command=True, help='Inicializa a execução do servidor Minecraft Pocket')
    #@commands.hybrid_command()
    async def startmineserverpocket(self, ctx:commands.Context):
        if self.status == True:
            await ctx.send(f"{self.servername} O Servidor está em manutenção. Retornaremos assim que possível")

        else:

            try:
                # Verifica se o processo java.exe está em execução
                process_name = "bedrock_server.exe"
                process_running = any(process_name.lower() in p.name().lower() for p in psutil.process_iter())
                ip = await self.get_external_ip()


                if process_running:
                    await ctx.send("O servidor já está em execução.")
                    #await ctx.send(f"{self.servername} Servidor ligado! ✅ Entre na opção **Multijogador** e adicione o IP: `{ip}:{self.serverport}`")
                    return

                else:
                    server_exe_path = r"E:\MINECRAFT_BEDROCK\StartBedrockServer.bat"
                    subprocess.Popen(server_exe_path, creationflags=subprocess.CREATE_NEW_CONSOLE)  # Inicia o programa em segundo plano
                    await ctx.send("Servidor iniciando, por favor aguarde...")
                    print("Servidor iniciando, por favor aguarde...")
            except Exception as e:
                await ctx.send(f"Erro ao iniciar o servidor: {e}")
                print(f"Erro ao iniciar o servidor: {e}")
            
    def get_local_ip(self):
        try:
            # Criar um socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Conectar a um servidor qualquer para obter o IP local
            sock.connect(("8.8.8.8", 80))
            # Obter o endereço IP local a partir do socket
            local_ip = sock.getsockname()[0]
            # Fechar o socket
            sock.close()
            return local_ip
        except Exception as e:
            print(f"Erro ao obter o IP local: {e}")
            return None            
            
            

async def setup(bot):
    await bot.add_cog(ServerMineMonitorPocket(bot))