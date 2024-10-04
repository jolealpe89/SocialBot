#import os
#import discord
#from discord.ext import commands, tasks
#from datetime import datetime
#import mysql.connector
#import configparser
#from discord import app_commands
#from discord.ext.commands import Context
#
#class BirthdayCog(commands.Cog):
#    def __init__(self, bot):
#        self.bot = bot
#        self.config = self.load_config()
#        self.db_connection = self.connect_to_db()
#        self.create_table_if_not_exists()
#        self.check_birthdays_task = None
#        self.reset_flags_task = None
#        self.birthday_channels = self.load_channel_ids('aniversario/listas.txt')
#        self.wish_channels = self.load_channel_ids('aniversario/desejo.txt')
#
#    @commands.Cog.listener()
#    async def on_ready(self):
#        if not self.check_birthdays_task:
#            self.check_birthdays_task = self.check_birthdays.start()
#
#        if not self.reset_flags_task:
#            self.reset_flags_task = self.reset_flags.start()
#
#    def load_config(self):
#        config = configparser.ConfigParser()
#        config.read('verde/db_niver.ini')
#        return config['mysql']
#
#    def connect_to_db(self):
#        return mysql.connector.connect(
#            host=self.config['host'],
#            user=self.config['user'],
#            password=self.config['password'],
#            database=self.config['database']
#        )
#
#    def create_table_if_not_exists(self):
#        cursor = self.db_connection.cursor()
#        cursor.execute("""
#			CREATE TABLE IF NOT EXISTS birthdays (
#				user_id BIGINT NOT NULL,
#				server_id BIGINT NOT NULL,
#				day INT NOT NULL,
#				month INT NOT NULL,
#				flag CHAR(1) NOT NULL DEFAULT 'N'
#			)
#        """)
#        self.db_connection.commit()
#        cursor.close()
#
#    def load_channel_ids(self, file_path):
#        try:
#            with open(file_path, 'r', encoding='utf-8') as file:
#                return [int(line.strip()) for line in file.readlines()]
#        except FileNotFoundError:
#            return []
#
#    async def add_channel_id(self, file_path, channel_id):
#        with open(file_path, 'r+', encoding='utf-8') as file:
#            lines = [int(line.strip()) for line in file.readlines()]
#            if channel_id not in lines:
#                file.write(f"{channel_id}\n")
#
#    async def get_birthdays(self, server_id):
#        cursor = self.db_connection.cursor()
#        cursor.execute("SELECT user_id, day, month FROM birthdays WHERE server_id = %s ORDER BY month, day", (server_id,))
#        birthdays = cursor.fetchall()
#        cursor.close()
#        return birthdays
#
#    async def add_birthday_to_db(self, user_id, server_id, day, month):
#        cursor = self.db_connection.cursor()
#        cursor.execute("INSERT INTO birthdays (user_id, server_id, day, month) VALUES (%s, %s, %s, %s)", (user_id, server_id, day, month))
#        self.db_connection.commit()
#        cursor.close()
#
#    async def format_birthdays(self, server_id):
#        birthdays = await self.get_birthdays(server_id)
#        months = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
#        formatted_birthdays = {month: [] for month in months.values()}
#        
#        for user_id, day, month in birthdays:
#            user_mention = f"<@{user_id}>"
#            formatted_birthdays[months[month]].append(f"{user_mention} : {day:02d}")
#        
#        return formatted_birthdays
#
#    async def update_birthday_embed(self, channel, server_id):
#        formatted_birthdays = await self.format_birthdays(server_id)
#        embed = discord.Embed(title="Aniversários", color=discord.Color.purple())
#        embed2 = discord.Embed(title="Quer que o seu Aniversário também esteja aqui?", 
#                               description="Quer que seu aniversário esteja na lista? Use o comando /aniversario e coloque o dia e o mês do seu aniversário!", 
#                               color=discord.Color.purple())
#
#        # Obtém o emoji personalizado do servidor
#        guild = channel.guild
#        custom_emoji = discord.utils.get(guild.emojis, name='emoji_130')  # Substitua 'nome_do_emoji' pelo nome do seu emoji
#
#        # Verifica se o emoji foi encontrado e insere na descrição do embed2
#        if custom_emoji:
#            embed2.description += f" {custom_emoji}"  # Adiciona o emoji ao final da descrição
#        else:
#            embed2.description += "🎂"  # Caso não encontre, avisa que o emoji não foi encontrado
#
#        for month, birthday_list in formatted_birthdays.items():
#            if birthday_list:
#                embed.add_field(name=month, value="\n".join(birthday_list), inline=False)
#            else:
#                embed.add_field(name=month, value="-", inline=False)
#
#        # Configura a imagem do primeiro embed
#        embed.set_image(url='https://media.discordapp.net/attachments/1274837771021717514/1291084080913584168/IMG_5379.png?ex=66fecf40&is=66fd7dc0&hm=6fdd9c1fea188aa6a7b25995f39bb21dcf27193e611e4de89f9baf806f8dd1a0&=&format=webp&quality=lossless')
#        embed2.set_footer(text="Os Staffs agradecem.")
#
#        # Remove o embed antigo e envia o novo
#        await channel.purge()
#        await channel.send(embed=embed)
#        react = await channel.send(embed=embed2)
#        await react.add_reaction(custom_emoji)
#
#
#    @commands.hybrid_command(with_app_command=True)
#    @app_commands.describe(dia="O dia no formato de 1 a 31.", mes="Mês no formato de 1 a 12.")
#    async def aniversario(self, ctx: commands.Context, dia: int, mes: int):
#        """Adiciona um aniversário ao banco de dados para o servidor atual."""
#        if 1 <= dia <= 31 and 1 <= mes <= 12:
#            user_id = ctx.author.id
#            server_id = ctx.guild.id  # Obtém o ID do servidor atual
#
#            # Verifica se o aniversário já foi adicionado
#            if await self.check_birthday_exists(user_id, server_id):
#                await ctx.send("Você já cadastrou seu aniversário.", ephemeral=True)
#            else:
#                await self.add_birthday_to_db(user_id, server_id, dia, mes)
#                await ctx.send(f"Aniversário adicionado para {dia:02d}/{mes:02d}.", ephemeral=True)
#
#                # Atualiza o embed no canal de aniversários
#                channel = self.bot.get_channel(self.birthday_channels[0])  # Usa o primeiro ID de canal de aniversários
#                await self.update_birthday_embed(channel, server_id)
#        else:
#            await ctx.send("Data inválida. Por favor, insira um dia entre 1 e 31 e um mês entre 1 e 12.", ephemeral=True)
#
#    @commands.hybrid_command(with_app_command=True)
#    @app_commands.describe(usuario="O ID do usuário que será adicionado.", dia="O dia no formato de 1 a 31.", mes="Mês no formato de 1 a 12.")
#    @commands.has_permissions(administrator=True)
#    async def aniversario_add(self, ctx: commands.Context, usuario: discord.Member, dia: int, mes: int):
#        """Adiciona um aniversário ao banco de dados para o servidor atual."""
#        if 1 <= dia <= 31 and 1 <= mes <= 12:
#            user_id = usuario.id
#            server_id = ctx.guild.id  # Obtém o ID do servidor atual
#
#            # Verifica se o aniversário já foi adicionado
#            if await self.check_birthday_exists(user_id, server_id):
#                await ctx.send("Você já cadastrou seu aniversário.", ephemeral=True)
#            else:
#                await self.add_birthday_to_db(user_id, server_id, dia, mes)
#                await ctx.send(f"Aniversário adicionado para {dia:02d}/{mes:02d}.", ephemeral=True)
#
#                # Atualiza o embed no canal de aniversários
#                channel = self.bot.get_channel(self.birthday_channels[0])  # Usa o primeiro ID de canal de aniversários
#                await self.update_birthday_embed(channel, server_id)
#        else:
#            await ctx.send("Data inválida. Por favor, insira um dia entre 1 e 31 e um mês entre 1 e 12.", ephemeral=True)
#
#    @aniversario_add.error
#    async def aniversario_add_error(self, ctx: Context, error):
#        if isinstance(error, commands.MissingPermissions):
#            await ctx.send("Você não tem permissões para usar este comando.", ephemeral=True)
#
#
#
#    async def check_birthday_exists(self, user_id: int, server_id: int) -> bool:
#        """Verifica se o aniversário já foi adicionado para o usuário no servidor atual."""
#        cursor = self.db_connection.cursor()
#        query = """
#        SELECT 1 FROM birthdays 
#        WHERE user_id = %s AND server_id = %s
#        """
#        cursor.execute(query, (user_id, server_id))
#        result = cursor.fetchone()
#        cursor.close()
#        return result is not None
#
#
#    @tasks.loop(minutes=1)
#    async def check_birthdays(self):
#        """Verifica aniversários diariamente."""
#        now = datetime.now()
#        cursor = self.db_connection.cursor()
#        cursor.execute("SELECT user_id, server_id FROM birthdays WHERE day = %s AND month = %s AND flag = 'N'", (now.day, now.month))
#        todays_birthdays = cursor.fetchall()
#
#        for user_id, server_id in todays_birthdays:
#            user = self.bot.get_user(user_id)
#            server = self.bot.get_guild(server_id)
#            server_name = server.name
#            if user:
#                try:
#                    await user.send(f"Oiiiii, venho aqui em nome do servidor **{server_name}** te desejar feliz aniversário! Aproveite bem o seu dia!🎉")
#                except discord.Forbidden:
#                    pass  # Caso o bot não possa enviar DM ao usuário
#                
#            # Enviar mensagem no canal de desejar feliz aniversário
#            channel = self.bot.get_channel(self.wish_channels[0])  # Usa o primeiro ID de canal de desejar feliz aniversário
#            if channel:
#                await channel.send(f"# FELIZ ANIVERSÁRIOOOOOOOOOO <@{user_id}>!! Parabéns! 🎂")
#
#            # Atualiza a flag para 'E' após o envio
#            cursor.execute("UPDATE birthdays SET flag = 'E' WHERE user_id = %s AND server_id = %s", (user_id, server_id))
#
#        self.db_connection.commit()
#        cursor.close()
#
#    @check_birthdays.before_loop
#    async def before_check_birthdays(self):
#        await self.bot.wait_until_ready()
#
#    @tasks.loop(hours=24)
#    async def reset_flags(self):
#        """Reseta as flags de aniversário no início de um novo ano."""
#        now = datetime.now()
#        if now.month == 1 and now.day == 1:  # Verifica se é o primeiro dia do ano
#            cursor = self.db_connection.cursor()
#            cursor.execute("UPDATE birthdays SET flag = 'N'")
#            self.db_connection.commit()
#            cursor.close()
#
#    @reset_flags.before_loop
#    async def before_reset_flags(self):
#        await self.bot.wait_until_ready()
#
#    @commands.hybrid_command(with_app_command=True)
#    async def aniversariantes(self, ctx:commands.Context):
#        channel_id = ctx.channel.id
#
#        """Adiciona um canal para lista de aniversariantes."""
#        await self.add_channel_id('aniversario/listas.txt', channel_id)
#        await ctx.send(f"Canal de lista de aniversariantes adicionado: {channel_id}",ephemeral=True)
#
#    @commands.hybrid_command(with_app_command=True)
#    async def parabenizar(self, ctx:commands.Context):
#        channel_id = ctx.channel.id
#        """Adiciona um canal para enviar desejos de aniversário."""
#        await self.add_channel_id('aniversario/desejo.txt', channel_id)
#        await ctx.send(f"Canal de desejos de aniversário adicionado: {channel_id}",ephemeral=True)
#        await ctx.send()
#        
#
#async def setup(bot):
#    await bot.add_cog(BirthdayCog(bot))


import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import mysql.connector
import configparser
from discord import app_commands
from discord.ext.commands import Context

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.db_connection = self.connect_to_db()
        self.create_table_if_not_exists()
        self.check_birthdays_task = None
        self.reset_flags_task = None
        self.birthday_channels = self.load_channel_ids('aniversario/listas.txt')
        self.wish_channels = self.load_channel_ids('aniversario/desejo.txt')

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_birthdays_task:
            self.check_birthdays_task = self.check_birthdays.start()

        if not self.reset_flags_task:
            self.reset_flags_task = self.reset_flags.start()

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('verde/db_config.ini')
        return config['mysql']

    def connect_to_db(self):
        return mysql.connector.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database']
        )

    def create_table_if_not_exists(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
			CREATE TABLE IF NOT EXISTS birthdays (
				user_id BIGINT NOT NULL,
				server_id BIGINT NOT NULL,
				day INT NOT NULL,
				month INT NOT NULL,
				flag CHAR(1) NOT NULL DEFAULT 'N'
			)
        """)
        self.db_connection.commit()
        cursor.close()

    def load_channel_ids(self, file_path):
        channels_by_server = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file.readlines():
                    server_id, channel_id = map(int, line.strip().split(','))
                    if server_id not in channels_by_server:
                        channels_by_server[server_id] = []
                    channels_by_server[server_id].append(channel_id)
            
            return channels_by_server
        except FileNotFoundError:
            print("Erro ao encontrar arquivos")
            return {}

    async def add_channel_id(self, file_path, server_id, channel_id):
        with open(file_path, 'r+', encoding='utf-8') as file:
            lines = [int(line.strip()) for line in file.readlines()]
            if channel_id not in lines:
                file.write(f"{server_id},{channel_id}\n")

    async def get_birthdays(self, server_id):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT user_id, day, month FROM birthdays WHERE server_id = %s ORDER BY month, day", (server_id,))
        birthdays = cursor.fetchall()
        cursor.close()
        return birthdays

    async def add_birthday_to_db(self, user_id, server_id, day, month):
        cursor = self.db_connection.cursor()
        cursor.execute("INSERT INTO birthdays (user_id, server_id, day, month) VALUES (%s, %s, %s, %s)", (user_id, server_id, day, month))
        self.db_connection.commit()
        cursor.close()

    async def format_birthdays(self, server_id):
        birthdays = await self.get_birthdays(server_id)
        months = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        formatted_birthdays = {month: [] for month in months.values()}
        
        for user_id, day, month in birthdays:
            user_mention = f"<@{user_id}>"
            formatted_birthdays[months[month]].append(f"{user_mention} : {day:02d}")
        
        return formatted_birthdays

    async def update_birthday_embed(self, server_id):
        channels = self.birthday_channels.get(server_id)
        if channels:
            for channel_id in channels:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await self.update_birthday_embed_for_channel(channel, server_id)


    async def update_birthday_embed_for_channel(self, channel, server_id):
        formatted_birthdays = await self.format_birthdays(server_id)
        embed = discord.Embed(title="Aniversários", color=discord.Color.purple())
        embed2 = discord.Embed(title="Quer que o seu Aniversário também esteja aqui?", 
                               description="Quer que seu aniversário esteja na lista? Use o comando /aniversario e coloque o dia e o mês do seu aniversário!", 
                               color=discord.Color.purple())

        # Obtém o emoji personalizado do servidor
        guild = channel.guild
        custom_emoji = discord.utils.get(guild.emojis, name='emoji_130')  # Substitua 'nome_do_emoji' pelo nome do seu emoji

        # Verifica se o emoji foi encontrado e insere na descrição do embed2
        if custom_emoji:
            embed2.description += f" {custom_emoji}"  # Adiciona o emoji ao final da descrição
        else:
            embed2.description += "🎂"  # Caso não encontre, avisa que o emoji não foi encontrado

        for month, birthday_list in formatted_birthdays.items():
            if birthday_list:
                embed.add_field(name=month, value="\n".join(birthday_list), inline=False)
            else:
                embed.add_field(name=month, value="-", inline=False)

        # Configura a imagem do primeiro embed
        embed.set_image(url='https://media.discordapp.net/attachments/1274837771021717514/1291084080913584168/IMG_5379.png?ex=66fecf40&is=66fd7dc0&hm=6fdd9c1fea188aa6a7b25995f39bb21dcf27193e611e4de89f9baf806f8dd1a0&=&format=webp&quality=lossless')
        embed2.set_footer(text="Os Staffs agradecem.")

        # Remove o embed antigo e envia o novo
        await channel.purge()
        await channel.send(embed=embed)
        react = await channel.send(embed=embed2)
        await react.add_reaction(custom_emoji)


    @commands.hybrid_command(with_app_command=True)
    @app_commands.describe(dia="O dia no formato de 1 a 31.", mes="Mês no formato de 1 a 12.")
    async def aniversario(self, ctx: commands.Context, dia: int, mes: int):
        """Adiciona um aniversário ao banco de dados para o servidor atual."""
        if 1 <= dia <= 31 and 1 <= mes <= 12:
            user_id = ctx.author.id
            server_id = ctx.guild.id  # Obtém o ID do servidor atual

            # Verifica se o aniversário já foi adicionado
            if await self.check_birthday_exists(user_id, server_id):
                await ctx.send("Você já cadastrou seu aniversário.", ephemeral=True)
            else:
                await self.add_birthday_to_db(user_id, server_id, dia, mes)
                await ctx.send(f"Aniversário adicionado para {dia:02d}/{mes:02d}.", ephemeral=True)

                # Atualiza o embed no canal de aniversários
                #channel = self.bot.get_channel(self.birthday_channels[0])  # Usa o primeiro ID de canal de aniversários
                #await self.update_birthday_embed(channel, server_id)
                await self.update_birthday_embed(server_id)
        else:
            await ctx.send("Data inválida. Por favor, insira um dia entre 1 e 31 e um mês entre 1 e 12.", ephemeral=True)

    @commands.hybrid_command(with_app_command=True)
    @app_commands.describe(usuario="O ID do usuário que será adicionado.", dia="O dia no formato de 1 a 31.", mes="Mês no formato de 1 a 12.")
    @commands.has_permissions(administrator=True)
    async def aniversario_add(self, ctx: commands.Context, usuario: discord.Member, dia: int, mes: int):
        """Adiciona um aniversário ao banco de dados para o servidor atual."""
        if 1 <= dia <= 31 and 1 <= mes <= 12:
            user_id = usuario.id
            server_id = ctx.guild.id  # Obtém o ID do servidor atual

            # Verifica se o aniversário já foi adicionado
            if await self.check_birthday_exists(user_id, server_id):
                await ctx.send("Você já cadastrou seu aniversário.", ephemeral=True)
            else:
                await self.add_birthday_to_db(user_id, server_id, dia, mes)
                await ctx.send(f"Aniversário adicionado para {dia:02d}/{mes:02d}.", ephemeral=True)

                # Atualiza o embed no canal de aniversários
                channel = self.bot.get_channel(self.birthday_channels[0])  # Usa o primeiro ID de canal de aniversários
                await self.update_birthday_embed(channel, server_id)
        else:
            await ctx.send("Data inválida. Por favor, insira um dia entre 1 e 31 e um mês entre 1 e 12.", ephemeral=True)

    @aniversario_add.error
    async def aniversario_add_error(self, ctx: Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Você não tem permissões para usar este comando.", ephemeral=True)



    async def check_birthday_exists(self, user_id: int, server_id: int) -> bool:
        """Verifica se o aniversário já foi adicionado para o usuário no servidor atual."""
        cursor = self.db_connection.cursor()
        query = """
        SELECT 1 FROM birthdays 
        WHERE user_id = %s AND server_id = %s
        """
        cursor.execute(query, (user_id, server_id))
        result = cursor.fetchone()
        cursor.close()
        return result is not None


    @tasks.loop(minutes=1)
    async def check_birthdays(self):
        now = datetime.now()
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT user_id, server_id FROM birthdays WHERE day = %s AND month = %s AND flag = 'N'", (now.day, now.month))
        todays_birthdays = cursor.fetchall()

        for user_id, server_id in todays_birthdays:
            user = self.bot.get_user(user_id)
            server = self.bot.get_guild(server_id)
            server_name = server.name
            if user:
                try:
                    await user.send(f"Oiiiii, venho aqui em nome do servidor **{server_name}** te desejar feliz aniversário! Aproveite bem o seu dia!🎉")
                except discord.Forbidden:
                    pass
                
            channels = self.wish_channels.get(server_id)
            if channels:
                for channel_id in channels:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(f"# FELIZ ANIVERSÁRIOOOOOOOOOO <@{user_id}>!! Parabéns! 🎂")

            # Atualiza a flag para 'E' após o envio
            cursor.execute("UPDATE birthdays SET flag = 'E' WHERE user_id = %s AND server_id = %s", (user_id, server_id))

        self.db_connection.commit()
        cursor.close()


    @check_birthdays.before_loop
    async def before_check_birthdays(self):
        await self.bot.wait_until_ready()

    @tasks.loop(hours=24)
    async def reset_flags(self):
        """Reseta as flags de aniversário no início de um novo ano."""
        now = datetime.now()
        if now.month == 1 and now.day == 1:  # Verifica se é o primeiro dia do ano
            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE birthdays SET flag = 'N'")
            self.db_connection.commit()
            cursor.close()

    @reset_flags.before_loop
    async def before_reset_flags(self):
        await self.bot.wait_until_ready()

    @commands.hybrid_command(with_app_command=True)
    async def aniversariantes(self, ctx:commands.Context):
        channel_id = ctx.channel.id
        server_id = ctx.guild.id
        """Adiciona um canal para lista de aniversariantes."""
        await self.add_channel_id('aniversario/listas.txt', server_id, channel_id)
        await ctx.send(f"Canal de lista de aniversariantes adicionado: {channel_id}",ephemeral=True)

    @commands.hybrid_command(with_app_command=True)
    async def parabenizar(self, ctx:commands.Context):
        channel_id = ctx.channel.id
        server_id = ctx.guild.id
        """Adiciona um canal para enviar desejos de aniversário."""
        await self.add_channel_id('aniversario/desejo.txt', server_id, channel_id)
        await ctx.send(f"Canal de desejos de aniversário adicionado: {channel_id}",ephemeral=True)
        

async def setup(bot):
    await bot.add_cog(BirthdayCog(bot))