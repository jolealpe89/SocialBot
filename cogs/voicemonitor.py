from discord.ext import commands
from datetime import datetime
import os
import discord

class VoiceMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.monitored_servers = set()
        self.monitored_channels = set()

        # Carregar IDs de servidores e canais a partir dos arquivos
        self.load_monitored_servers()
        self.load_monitored_channels()

    def load_monitored_servers(self):
        try:
            with open('servers.txt', 'r', encoding='utf-8') as f:
                server_ids = set(map(int, f.read().split()))
                self.monitored_servers = server_ids
        except FileNotFoundError:
            pass

    def load_monitored_channels(self):
        try:
            with open('canais.txt', 'r', encoding='utf-8') as f:
                channel_ids = set(map(int, f.read().split()))
                self.monitored_channels = channel_ids
        except FileNotFoundError:
            pass

    async def log_to_server(self, server_id, message):
        current_time = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"``[{current_time}]`` {message}"

        # Gravação do log em arquivo
        log_folder = "X9"
        os.makedirs(log_folder, exist_ok=True)

        log_file_name = f"{server_id}-{datetime.now().strftime('%d-%m-%Y')}.txt"
        log_file_path = os.path.join(log_folder, log_file_name)

        with open(log_file_path, "a", encoding='utf-8') as log_file:
            log_file.write(formatted_message + "\n")

    async def log_to_channels(self, server_id, message):
        for channel_id in self.monitored_channels:
            channel = self.bot.get_channel(channel_id)
            if channel and channel.guild.id == server_id:
                await channel.send(message)
                await self.log_to_server(server_id, message)

    @commands.hybrid_command(with_app_command=True, name='monitorar', help='Adiciona o canal atual na lista de monitoramento.')
    async def monitorar(self, ctx: commands.Context):
        server_id = ctx.guild.id
        if server_id not in self.monitored_servers:
            self.monitored_servers.add(server_id)
            with open('servers.txt', 'a', encoding='utf-8') as f:
                f.write(str(server_id) + '\n')

        if ctx.channel.id not in self.monitored_channels:
            self.monitored_channels.add(ctx.channel.id)
            with open('canais.txt', 'a', encoding='utf-8') as f:
                f.write(str(ctx.channel.id) + '\n')

        await ctx.send('Servidor e canal adicionados aos monitorados.')

    @commands.hybrid_command(with_app_command=True, name='desmonitorar', help='Remove o canal atual na lista de monitoramento.')
    async def desmonitorar(self, ctx: commands.Context):
        server_id = ctx.guild.id
        if server_id in self.monitored_servers:
            self.monitored_servers.remove(server_id)
            with open('servers.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(map(str, self.monitored_servers)))

        if ctx.channel.id in self.monitored_channels:
            self.monitored_channels.remove(ctx.channel.id)
            with open('canais.txt', 'w', encoding='utf-8') as f:
                f.write('\n'.join(map(str, self.monitored_channels)))

        await ctx.send('Servidor e canal removidos dos monitorados.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        server_id = member.guild.id
        
        if server_id in self.monitored_servers and before.channel != after.channel:
            if after.channel:  # Quando o membro entra ou é movido para um canal
                channel_link = f"https://discord.com/channels/{member.guild.id}/{after.channel.id}"
                message = f'**{member.display_name}** entrou no canal de voz {channel_link}'
            elif before.channel:  # Quando o membro sai do canal
                message = f'**{member.display_name}** saiu do canal de voz **{before.channel.name}**'
            
            await self.log_to_channels(server_id, message)

#    @commands.Cog.listener()
#    async def on_voice_state_update(self, member, before, after):
#        server_id = member.guild.id
#        if server_id in self.monitored_servers and before.channel != after.channel:
#            message = None
#
#            if after.channel:
#                if before.channel is not None:  # Se o membro foi movido de um canal para outro
#                    # Verifica o log de auditoria para encontrar quem moveu o membro
#                    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.member_move):
#                        if entry.target is not None and entry.target.id == member.id:
#                            mover = entry.user
#                            message = f'**{mover.display_name}** moveu **{member.display_name}** para o canal de voz **{after.channel.name}**'
#                            break
#
#                if message is None:  # Caso o membro não tenha sido movido por outro usuário
#                    message = f'**{member.display_name}** entrou no canal de voz **{after.channel.name}**'
#
#            elif before.channel:
#                message = f'**{member.display_name}** saiu do canal de voz **{before.channel.name}**'
#
#            if message:
#                await self.log_to_channels(server_id, message)



    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        audit_log_entry = None
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target == user:
                audit_log_entry = entry
                break
            
        server_id = guild.id
        if server_id in self.monitored_servers:
            if audit_log_entry:
                ban_author = audit_log_entry.user
                ban_reason = audit_log_entry.reason if audit_log_entry.reason else "sem motivo especificado"
                
                message = f'**{user.display_name}** foi banido do servidor por **{ban_author.display_name}**\n\n**Motivo:** {ban_reason}.'
            else:
                message = f'**{user.display_name}** foi banido do servidor.'

            await self.log_to_channels(server_id, message)


async def setup(bot):
    await bot.add_cog(VoiceMonitor(bot))
#import discord
#from discord.ext import commands
#from datetime import datetime
#import os
#
#class VoiceMonitor(commands.Cog):
#    def __init__(self, bot):
#        self.bot = bot
#        self.monitored_servers = set()
#        self.monitored_channels = set()
#
#        # Carregar IDs de servidores e canais a partir dos arquivos
#        self.load_monitored_servers()
#        self.load_monitored_channels()
#
#    def load_monitored_servers(self):
#        try:
#            with open('servers.txt', 'r', encoding='utf-8') as f:
#                server_ids = set(map(int, f.read().split()))
#                self.monitored_servers = server_ids
#        except FileNotFoundError:
#            pass
#
#    def load_monitored_channels(self):
#        try:
#            with open('canais.txt', 'r', encoding='utf-8') as f:
#                channel_ids = set(map(int, f.read().split()))
#                self.monitored_channels = channel_ids
#        except FileNotFoundError:
#            pass
#
#    async def log_to_server(self, server_id, message):
#        current_time = datetime.now().strftime("%H:%M:%S")
#        formatted_message = f"``[{current_time}]`` {message}"
#
#        # Gravação do log em arquivo
#        log_folder = "X9"
#        os.makedirs(log_folder, exist_ok=True)
#
#        log_file_name = f"{server_id}-{datetime.now().strftime('%d-%m-%Y')}.txt"
#        log_file_path = os.path.join(log_folder, log_file_name)
#
#        with open(log_file_path, "a", encoding='utf-8') as log_file:
#            log_file.write(formatted_message + "\n")
#
#    async def log_to_channels(self, server_id, message):
#        for channel_id in self.monitored_channels:
#            channel = self.bot.get_channel(channel_id)
#            if channel and channel.guild.id == server_id:
#                await channel.send(message)
#                await self.log_to_server(server_id, message)
#
#    @commands.hybrid_command(with_app_command=True, name='monitorar', help='Adiciona o canal atual na lista de monitoramento.')
#    async def monitorar(self, ctx: commands.Context):
#        server_id = ctx.guild.id
#        if server_id not in self.monitored_servers:
#            self.monitored_servers.add(server_id)
#            with open('servers.txt', 'a', encoding='utf-8') as f:
#                f.write(str(server_id) + '\n')
#
#        if ctx.channel.id not in self.monitored_channels:
#            self.monitored_channels.add(ctx.channel.id)
#            with open('canais.txt', 'a', encoding='utf-8') as f:
#                f.write(str(ctx.channel.id) + '\n')
#
#        await ctx.send('Servidor e canal adicionados aos monitorados.')
#
#    @commands.hybrid_command(with_app_command=True, name='desmonitorar', help='Remove o canal atual na lista de monitoramento.')
#    async def desmonitorar(self, ctx: commands.Context):
#        server_id = ctx.guild.id
#        if server_id in self.monitored_servers:
#            self.monitored_servers.remove(server_id)
#            with open('servers.txt', 'w', encoding='utf-8') as f:
#                f.write('\n'.join(map(str, self.monitored_servers)))
#
#        if ctx.channel.id in self.monitored_channels:
#            self.monitored_channels.remove(ctx.channel.id)
#            with open('canais.txt', 'w', encoding='utf-8') as f:
#                f.write('\n'.join(map(str, self.monitored_channels)))
#
#        await ctx.send('Servidor e canal removidos dos monitorados.')
#
#    @commands.Cog.listener()
#    async def on_voice_state_update(self, member, before, after):
#        server_id = member.guild.id
#        if server_id in self.monitored_servers:
#            if before.channel != after.channel:
#                if before.channel and after.channel:
#                    mover = None
#                    for m in before.channel.members:
#                        if m.guild_permissions.move_members and m != member:
#                            mover = m
#                            break
#                    if mover:
#                        message = f'**{mover.display_name}** moveu **{member.display_name}** para o canal de voz **{after.channel.name}**'# no servidor **{member.guild.name}**.'
#                        await self.log_to_channels(server_id, message)
#                    else:
#                        message = f'**{member.display_name}** entrou no canal de voz **{after.channel.name}**'# no servidor **{member.guild.name}**.'
#                        await self.log_to_channels(server_id, message)
#                elif after.channel:
#                    message = f'**{member.display_name}** entrou no canal de voz **{after.channel.name}**'# no servidor **{member.guild.name}**.'
#                    await self.log_to_channels(server_id, message)
#                elif before.channel:
#                    message = f'**{member.display_name}** saiu do canal de voz **{before.channel.name}**'# no servidor **{member.guild.name}**.'
#                    await self.log_to_channels(server_id, message)
#            elif before.channel and not after.channel:
#                disconnector = None
#                for m in before.channel.members:
#                    if m.guild_permissions.move_members and m != member:
#                        disconnector = m
#                        break
#                if disconnector:
#                    message = f'**{disconnector.display_name}** desconectou **{member.display_name}** do canal de voz **{before.channel.name}**'# no servidor **{member.guild.name}**.'
#                    await self.log_to_channels(server_id, message)
#
#    #@commands.Cog.listener()
#    #async def on_member_remove(self, member):
#    #    server_id = member.guild.id
#    #    if server_id in self.monitored_servers:
#    #        message = f'**{member.display_name}** foi expulso do servidor **{member.guild.name}**.'
#    #        await self.log_to_channels(server_id, message)
#
##    @commands.Cog.listener()
##    async def on_member_ban(self, guild, user):
##        server_id = guild.id
##        if server_id in self.monitored_servers:
##            message = f'**{user.display_name}** foi banido do servidor **{guild.name}**.'
##            await self.log_to_channels(server_id, message)
#
#
#    @commands.Cog.listener()
#    async def on_member_ban(self, guild, user):
#        audit_log_entry = None
#        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
#            if entry.target == user:
#                audit_log_entry = entry
#                break
#            
#        server_id = guild.id
#        if server_id in self.monitored_servers:
#            if audit_log_entry:
#                ban_author = audit_log_entry.user
#                ban_reason = audit_log_entry.reason if audit_log_entry.reason else "sem motivo especificado"
#                
#                message = f'**{user.display_name}** foi banido do servidor por **{ban_author.display_name}**\n\n**Motivo:** {ban_reason}.'
#            else:
#                message = f'**{user.display_name}** foi banido do servidor.'
#
#            await self.log_to_channels(server_id, message)
#
#async def setup(bot):
#    await bot.add_cog(VoiceMonitor(bot))