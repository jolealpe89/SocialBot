import discord
from discord.ext import commands
from discord.ext.commands import Context
import random
import os
import json

prefixo = ',b'

class AdministradorDeCargos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_folder_structure(self, guild_id):
        # Criar diretório da classe
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)

        # Criar diretório do servidor se não existir
        server_dir = os.path.join(class_dir, str(guild_id))
        if not os.path.exists(server_dir):
            os.makedirs(server_dir)

        # Criar o arquivo 'dicionario.txt' se não existir
        dicionario_file = os.path.join(server_dir, 'dicionario.txt')
        if not os.path.exists(dicionario_file):
            with open(dicionario_file, 'w', encoding='utf-8'):
                pass

        # Criar o arquivo 'MessagesIDs.txt' se não existir
        messages_id_file = os.path.join(server_dir, 'MessagesIDs.txt')
        if not os.path.exists(messages_id_file):
            with open(messages_id_file, 'w', encoding='utf-8'):
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild_id = payload.guild_id
        await self.create_folder_structure(guild_id)
        
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        server_dir = os.path.join(class_dir, str(guild_id))
        message_ids = []
        
        try:
            with open(os.path.join(server_dir, 'MessagesIDs.txt'), 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        message_ids.append(int(line))
        except FileNotFoundError:
            print(f'Arquivo MessagesIDs.txt não encontrado para o servidor {guild_id}.')
            return
        
        if payload.message_id not in message_ids:
            return
        
        emoji_roles = {}
        with open(os.path.join(server_dir, 'dicionario.txt'), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    emoji, role = line.split(':')
                    emoji_roles[emoji] = role
        
        guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
        role_name = emoji_roles.get(str(payload.emoji))
        
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)

            # Cria o cargo caso ele não exista
            if role is None:
                role = await guild.create_role(name=role_name, color=discord.Color(random.randint(0, 0xFFFFFF)))

            member = guild.get_member(payload.user_id)
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild_id = payload.guild_id
        await self.create_folder_structure(guild_id)
        
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        server_dir = os.path.join(class_dir, str(guild_id))
        message_ids = []
        
        try:
            with open(os.path.join(server_dir, 'MessagesIDs.txt'), 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        message_ids.append(int(line))
        except FileNotFoundError:
            print(f'Arquivo MessagesIDs.txt não encontrado para o servidor {guild_id}.')
            return
        
        if payload.message_id not in message_ids:
            return
        
        emoji_roles = {}
        with open(os.path.join(server_dir, 'dicionario.txt'), 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    emoji, role = line.split(':')
                    emoji_roles[emoji] = role
        
        guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
        role_name = emoji_roles.get(str(payload.emoji))
        
        if role_name is not None:
            role = discord.utils.get(guild.roles, name=role_name)

            if role is not None:
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)

#    @commands.Cog.listener()
#    async def on_member_remove(self, member):
#        try:
#            await self.send_goodbye_message(member, member.guild.name)
#        except discord.errors.Forbidden:
#            print(f"Não foi possível enviar mensagem para {member.name}, permissão negada.")
#
#    async def send_goodbye_message(self, member, guild_name):
#        default_message = f'Até logo, {member.name}! Você saiu do servidor {guild_name}.'
#        try:
#            await member.send(default_message)
#        except discord.errors.Forbidden:
#            print(f"Não foi possível enviar mensagem para {member.name}, permissão negada.")

#    @commands.command(name='createembed', help='Um comando que cria mensagens embed. Muito chique.')
#    async def create_embed(self, ctx):
#        guild_id = str(ctx.guild.id)
#        await self.create_folder_structure(guild_id)
#        
#        def check(msg):
#            return msg.author == ctx.author and msg.channel == ctx.channel
#        
#        await ctx.send("Vamos criar uma mensagem embed. Digite o título:")
#        title_msg = await self.bot.wait_for('message', check=check, timeout=60)
#        title = title_msg.content
#        
#        await ctx.send("Agora, digite a descrição:")
#        description_msg = await self.bot.wait_for('message', check=check, timeout=60)
#        description = description_msg.content
#        
#        await ctx.send("Escolha uma cor hexadecimal para a borda da embed (por exemplo, ff0000) ou envie 'R' para uma cor aleatória:")
#        color_msg = await self.bot.wait_for('message', check=check, timeout=60)
#        
#        if color_msg.content.lower() == 'r':
#            color = discord.Color(random.randint(0, 0xFFFFFF))
#        else:
#            color = discord.Color(int(color_msg.content, 16))
#
#
#        embed = discord.Embed(
#            title=title,
#            description=description,
#            color=color
#        )
#        embed.set_footer(text='Reaja abaixo:')
#
#        await ctx.send("Agora, digite os emojis que você deseja adicionar à mensagem (separados por espaço):")
#        emojis_msg = await self.bot.wait_for('message', check=check, timeout=600)
#        emojis = emojis_msg.content.split()
#
#        await ctx.channel.purge(limit=9, check=lambda msg: msg.author == self.bot.user or msg.author == ctx.author)
#        message = await ctx.send(embed=embed)
#        
#        for emoji in emojis:
#            await message.add_reaction(emoji)
    @commands.command(name='createembed', help='Um comando que cria mensagens embed. Muito chique.')
    async def create_embed(self, ctx):
        guild_id = str(ctx.guild.id)
        await self.create_folder_structure(guild_id)

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        await ctx.send("Vamos criar uma mensagem embed. Digite o título:")
        title_msg = await self.bot.wait_for('message', check=check, timeout=60)
        title = title_msg.content

        await ctx.send("Agora, digite a descrição:")
        description_msg = await self.bot.wait_for('message', check=check, timeout=60)
        description = description_msg.content

        await ctx.send("Escolha uma cor hexadecimal para a borda da embed (por exemplo, ff0000) ou envie 'R' para uma cor aleatória:")
        color_msg = await self.bot.wait_for('message', check=check, timeout=60)

        if color_msg.content.lower() == 'r':
            color = discord.Color(random.randint(0, 0xFFFFFF))
        else:
            color = discord.Color(int(color_msg.content, 16))

        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        await ctx.send("Deseja adicionar uma imagem ao embed? Envie o link ou anexe a imagem. Se não quiser, envie 'P':")
        image_msg = await self.bot.wait_for('message', check=check, timeout=60)
        if image_msg.content.lower() != 'p':
            if image_msg.attachments:
                embed.set_image(url=image_msg.attachments[0].url)
            else:
                embed.set_image(url=image_msg.content)

        await ctx.send("Deseja adicionar uma thumbnail ao embed? Envie o link ou anexe a imagem. Se não quiser, envie 'P':")
        thumbnail_msg = await self.bot.wait_for('message', check=check, timeout=60)
        if thumbnail_msg.content.lower() != 'p':
            if thumbnail_msg.attachments:
                embed.set_thumbnail(url=thumbnail_msg.attachments[0].url)
            else:
                embed.set_thumbnail(url=thumbnail_msg.content)

        await ctx.send("Deseja adicionar uma mensagem no footer do embed? Se sim, digite a mensagem. Se não quiser, envie 'P':")
        footer_msg = await self.bot.wait_for('message', check=check, timeout=60)
        if footer_msg.content.lower() != 'p':
            embed.set_footer(text=footer_msg.content)

        await ctx.send("Agora, digite os emojis que você deseja adicionar à mensagem (separados por espaço) ou envie 'P' para pular esta etapa:")
        emojis_msg = await self.bot.wait_for('message', check=check, timeout=600)
        if emojis_msg.content.lower() != 'p':
            emojis = emojis_msg.content.split()

        await ctx.channel.purge(limit=15, check=lambda msg: msg.author == self.bot.user or msg.author == ctx.author)
        message = await ctx.send(embed=embed)

        if emojis_msg.content.lower() != 'p':
            for emoji in emojis:
                await message.add_reaction(emoji)




    @commands.command(name='editarmensagem', help='Edita uma mensagem do bot por ID')
    async def editar_mensagem(self, ctx, message_id: int, *, nova_mensagem):
        try:
            message = await ctx.channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.send(f'Mensagem com ID {message_id} não encontrada.')
            return

        if message.author != self.bot.user:
            await ctx.send('Você só pode editar mensagens enviadas pelo bot.')
            return

        nova_mensagem = nova_mensagem.replace('@', f'@{ctx.guild.me.display_name}')
        await message.edit(content=nova_mensagem)
        await ctx.send(f'Mensagem editada com sucesso: {message.jump_url}')

    @commands.command(name='inserirdicionario', help='Insere valores no arquivo "dicionario.txt"')
    async def inserir_dicionario(self, ctx, *, dicionario):
        guild_id = str(ctx.guild.id)
        await self.create_folder_structure(guild_id)
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        directory = os.path.join(class_dir, guild_id)

        with open(os.path.join(directory, 'dicionario.txt'), 'a', encoding='utf-8') as f:
            f.write(f'{dicionario}\n')
        await ctx.send('Dicionário inserido com sucesso!')

    @commands.command(name='inserirmessageid', help='Insere valores no arquivo "MessagesIDs.txt"')
    async def inserir_message_id(self, ctx, *, mensagem: str):
        guild_id = str(ctx.guild.id)
        await self.create_folder_structure(guild_id)
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        directory = os.path.join(class_dir, guild_id)

        with open(os.path.join(directory, 'MessagesIDs.txt'), 'a', encoding='utf-8') as f:
            f.write(f'{mensagem}\n')
        await ctx.send('ID da mensagem inserido com sucesso!')

        
    # Função para excluir um número de linhas definido pelo usuário do arquivo "MessagesID.txt"
    @commands.command(name='excluirmessageid', help='Exclui um número de linhas definido pelo usuário de "MessagesID.txt"')
    async def excluir_message_id(self, ctx, num_linhas: int):
        guild_id = str(ctx.guild.id)
        server_dir = os.path.join(os.getcwd(), type(self).__name__, guild_id)
        messages_id_file = os.path.join(server_dir, 'MessagesIDs.txt')

        with open(messages_id_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open(messages_id_file, 'w', encoding='utf-8') as f:
            f.writelines(lines[:-num_linhas])
        await ctx.send(f'{num_linhas} linhas removidas de "MessagesIDs.txt".')

    # Função para excluir um número de linhas definido pelo usuário do arquivo "dicionario.txt"
    @commands.command(name='excluirdicionario', help='Exclui um número de linhas definido pelo usuário do arquivo "dicionario.txt"')
    async def excluir_dicionario(self, ctx, num_linhas: int):
        guild_id = str(ctx.guild.id)
        server_dir = os.path.join(os.getcwd(), type(self).__name__, guild_id)
        dicionario_file = os.path.join(server_dir, 'dicionario.txt')

        with open(dicionario_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open(dicionario_file, 'w', encoding='utf-8') as f:
            f.writelines(lines[:-num_linhas])
        await ctx.send(f'{num_linhas} linhas removidas de "dicionario.txt".')

    # Função para excluir o arquivo "MessagesIDs.txt"
    @commands.command(name='excluirmessagesidfile', help='Exclui o arquivo "MessagesIDs.txt"')
    async def excluir_messages_id(self, ctx):
        guild_id = str(ctx.guild.id)
        server_dir = os.path.join(os.getcwd(), type(self).__name__, guild_id)
        messages_id_file = os.path.join(server_dir, 'MessagesIDs.txt')

        os.remove(messages_id_file)
        await ctx.send('"MessagesID.txt" removido.')

    # Função para excluir o arquivo "dicionario.txt"
    @commands.command(name='excluirdicionariofile', help='Exclui o arquivo "dicionario.txt"')
    async def excluir_dicionario_file(self, ctx):
        guild_id = str(ctx.guild.id)
        server_dir = os.path.join(os.getcwd(), type(self).__name__, guild_id)
        dicionario_file = os.path.join(server_dir, 'dicionario.txt')

        os.remove(dicionario_file)
        await ctx.send('"dicionario.txt" removido.')

    # Função para exibir o conteúdo do arquivo "dicionario.txt"
    @commands.command(name='mostrardicionario', help='Mostra o conteúdo do arquivo "dicionario.txt"')
    async def mostrar_dicionario(self, ctx):
        guild_id = str(ctx.guild.id)
        server_dir = os.path.join(os.getcwd(), type(self).__name__, guild_id)
        dicionario_file = os.path.join(server_dir, 'dicionario.txt')

        with open(dicionario_file, 'r', encoding='utf-8') as f:
            content = f.read()
        await ctx.send(f'Conteúdo de "dicionario.txt":\n```\n{content}\n```')

    
    # Função para exibir o conteúdo do arquivo "MessagesID.txt" com os links para as mensagens
    @commands.command(name='mostrarmessagesid', help='Mostra os números e links das mensagens do arquivo "MessagesID.txt"')
    async def mostrar_messages_id(self, ctx):
        guild_id = str(ctx.guild.id)
        server_dir = os.path.join(os.getcwd(), type(self).__name__, guild_id)
        messages_id_file = os.path.join(server_dir, 'MessagesIDs.txt')

        with open(messages_id_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        message_links = []
        for idx, line in enumerate(lines, start=1):
            message_id = line.strip()
            try:
                message_link = f'[Link da Mensagem {idx}](https://discordapp.com/channels/{ctx.guild.id}/{ctx.channel.id}/{message_id})'
                message_links.append(f"message_id: {message_id}\nLink: {message_link}")
            except Exception as e:
                print(f"Erro ao gerar link para mensagem ID {message_id}: {e}")

        if message_links:
            message_links_str = '\n\n'.join(message_links)
            await ctx.send(f'Informações das mensagens em "MessagesID.txt":\n\n{message_links_str}\n')
        else:
            await ctx.send('Nenhuma mensagem encontrada em "MessagesID.txt".')

    @commands.hybrid_command(with_app_command=True, help='Cria um ou mais cargos. Envie separados por vírgula.')
    @commands.has_permissions(administrator=True)
    async def create_roles(self, ctx: Context, *, roles: str):
        await ctx.send("Ok!")
        role_names = [role.strip() for role in roles.split(',')]
        created_roles = []

        for role_name in role_names:
            try:
                # Gera uma cor aleatória
                random_color = discord.Color(random.randint(0x000000, 0xFFFFFF))
                # Cria o cargo no servidor com a cor aleatória
                new_role = await ctx.guild.create_role(name=role_name, color=random_color)
                created_roles.append(new_role)
            except discord.DiscordException as e:
                await ctx.send(f"Erro ao criar o cargo {role_name}: {e}")
        
        if created_roles:
            created_role_names = ', '.join(role.name for role in created_roles)
            await ctx.send(f"Os seguintes cargos foram criados com sucesso: {created_role_names}")
        else:
            await ctx.send("Nenhum cargo foi criado.")

    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(manage_roles=True)
    async def create_cores(self, ctx: commands.Context):
        # Definir o caminho para o arquivo cores.json dentro da pasta 'ColorsCargos'
        caminho_arquivo = os.path.join('ColorsCargos', 'cores.json')

        # Carregar o arquivo JSON com os nomes e as cores
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        # Iterar sobre as cores e criar os cargos com base nas informações do arquivo
        for cor in dados["cores"]:
            nome = cor["nome"]
            hex_color = cor["hex"]
            
            # Se a cor for "R" ou "r", gerar uma cor hexadecimal aleatória
            if hex_color.lower() == "r":
                random_color = discord.Color(random.randint(0, 0xFFFFFF))
            else:
                # Caso contrário, usar a cor hexadecimal fornecida
                random_color = discord.Color(int(hex_color, 16))
            
            # Criar o cargo no servidor
            await ctx.guild.create_role(name=nome, color=random_color)
            await ctx.send(f"Criado o cargo: **{nome}** com a cor {random_color}.", ephemeral=True)
    
        await ctx.send("Todos os cargos foram criados com sucesso!", ephemeral=True)

    @create_cores.error
    async def create_cores_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permissões para usar este comando.", ephemeral=True)


    @create_roles.error
    async def create_roles_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permissões para usar este comando.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdministradorDeCargos(bot))