#import random
#from discord.ext import commands
#import discord
#import random
#
#
#
#
#class SortearPinto(commands.Cog):
#    def __init__(self, bot):
#        self.bot = bot
#
#
#    @commands.hybrid_command(with_app_command=True, help='Sorteia um tamanho de pinto pra você.')
#    async def pinto(self, ctx:commands.Context):
#
#        numero_sorteado = random.randint(1, 50)
#        embed = discord.Embed(title=f"{ctx.author.display_name} tem", description=f"# {numero_sorteado} cm de pau.", color=0x0000FF)
#        embed.set_image(url='https://opresenterural.com.br/wp-content/uploads/2019/05/pintinho2-e1558016678542.jpg')
#        if numero_sorteado <= 2:
#            mensagem ="Uma clitóris avantajada!?"
#        elif numero_sorteado <= 13:
#            mensagem ="Pequetuxo."
#        elif numero_sorteado <= 20:
#            mensagem ="Está na média."
#        elif numero_sorteado <= 30:
#            mensagem ="O dote!"
#        elif numero_sorteado <= 50:
#            mensagem ="Caramba! Como cabe isso na calça?"
#
#        embed.set_footer(text=mensagem)
#        embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
#        await ctx.send(embed=embed)
#
#async def setup(bot):
#    await bot.add_cog(SortearPinto(bot))

#import random
#from discord.ext import commands
#import discord
#import os
#from openpyxl import Workbook, load_workbook
#from datetime import datetime
#
#class PintoGame(commands.Cog):
#    def __init__(self, bot):
#        self.bot = bot
#        self.file_name = f'D:\DISCORD_BOTS\Social_Hub\SocialBot\Pinto\pinto_placar_{datetime.now().strftime("%Y-%m-%d")}.xlsx'
#
#        # Se a planilha não existir, cria uma nova com as colunas adequadas
#        if not os.path.exists(self.file_name):
#            self.create_excel()
#
#    def create_excel(self):
#        wb = Workbook()
#        ws = wb.active
#        ws.title = "Placar"
#        ws.append(["Posição", "Jogador", "Tamanho do Pinto (cm)"])
#        wb.save(self.file_name)
#
#    def update_placar(self, player_name, size):
#        try:
#            wb = load_workbook(self.file_name)
#            ws = wb.active
#
#            # Verifica se o jogador já está no placar
#            player_in_placar = False
#            for row in range(2, ws.max_row + 1):
#                if ws[f'B{row}'].value == player_name:
#                    ws[f'C{row}'] = size  # Atualiza o tamanho do pinto
#                    player_in_placar = True
#                    break
#
#            # Se o jogador não estiver no placar, adiciona ele
#            if not player_in_placar:
#                new_row = [ws.max_row + 1, player_name, size]
#                ws.append(new_row)
#
#            # Ordena o placar pela coluna de tamanho do pinto, garantindo que os valores de tamanho são numéricos
#            placar_data = [(row[0], row[1], row[2] if isinstance(row[2], int) else 0) for row in ws.iter_rows(min_row=2, values_only=True)]
#            sorted_data = sorted(placar_data, key=lambda x: x[2], reverse=True)
#
#            # Limpa o placar e escreve novamente os dados ordenados
#            for row in ws.iter_rows(min_row=2):
#                for cell in row:
#                    cell.value = None
#
#            for idx, data in enumerate(sorted_data, start=1):
#                ws[f'A{idx + 1}'] = idx
#                ws[f'B{idx + 1}'] = data[1]
#                ws[f'C{idx + 1}'] = data[2]
#
#            wb.save(self.file_name)
#        except Exception as e:
#            print(f"Erro ao atualizar placar: {e}")
#
#    def get_player_size(self, player_name):
#        wb = load_workbook(self.file_name)
#        ws = wb.active
#
#        for row in ws.iter_rows(min_row=2, values_only=True):
#            if row[1] == player_name:
#                return row[2]
#        return None
#
#    @commands.hybrid_command(with_app_command=True, help='Sorteia um tamanho de pinto para você.')
#    async def pinto(self, ctx: commands.Context):
#        player_name = ctx.author.display_name
#        size = random.randint(1, 50)
#
#        embed = discord.Embed(title=f"{ctx.author.display_name} tem", description=f"{size} cm de pau.", color=0x0000FF)
#        embed.set_image(url='https://opresenterural.com.br/wp-content/uploads/2019/05/pintinho2-e1558016678542.jpg')
#
#        if size <= 2:
#            mensagem = "Uma clitóris avantajada!?"
#        elif size <= 13:
#            mensagem = "Pequetuxo."
#        elif size <= 20:
#            mensagem = "Está na média."
#        elif size <= 30:
#            mensagem = "O dote!"
#        else:
#            mensagem = "Caramba! Como cabe isso na calça?"
#
#        embed.set_footer(text=mensagem)
#        embed.set_thumbnail(url=ctx.author.display_avatar)
#
#        await ctx.send(embed=embed)
#        self.update_placar(player_name, size)
#
#    @commands.hybrid_command(with_app_command=True, help='Desafia outro jogador para um duelo de pintos.')
#    async def duelo(self, ctx: commands.Context, opponent: discord.Member):
#        challenger = ctx.author.display_name
#        opponent_name = opponent.display_name
#
#        challenger_size = self.get_player_size(challenger)
#        opponent_size = self.get_player_size(opponent_name)
#
#        if challenger_size is None:
#            await ctx.send(f"{ctx.author.mention}, você precisa sortear seu pinto primeiro usando `/pinto`.")
#            return
#        if opponent_size is None:
#            await ctx.send(f"{opponent.mention}, você precisa sortear seu pinto primeiro usando `/pinto`.")
#            return
#
#        # Simulação do duelo
#        challenger_roll = random.randint(1, 100)
#        opponent_roll = random.randint(1, 100)
#
#        if challenger_roll > opponent_roll:
#            await ctx.send(f"🎉 {challenger} venceu o duelo! Ganhou 1 cm de pinto.")
#            self.update_placar(challenger, challenger_size + 1)
#            self.update_placar(opponent_name, max(1, opponent_size - 1))  # O pinto não pode ser menor que 1 cm
#        elif opponent_roll > challenger_roll:
#            await ctx.send(f"🎉 {opponent_name} venceu o duelo! Ganhou 1 cm de pinto.")
#            self.update_placar(opponent_name, opponent_size + 1)
#            self.update_placar(challenger, max(1, challenger_size - 1))
#        else:
#            await ctx.send("O duelo terminou empatado! Ninguém ganha ou perde centímetros.")
#
#    @commands.hybrid_command(with_app_command=True, help='Exibe o placar atual dos maiores pintos.')
#    async def placar(self, ctx: commands.Context):
#        try:
#            wb = load_workbook(self.file_name)
#            ws = wb.active
#
#            placar_texto = ""
#            for row in ws.iter_rows(min_row=2, values_only=True):
#                placar_texto += f"{row[0]}. {row[1]} - {row[2]} cm\n"
#
#            embed = discord.Embed(title="Placar dos Maiores Pintos", description=placar_texto, color=0x00FF00)
#            await ctx.send(embed=embed)
#        except Exception as e:
#            await ctx.send(f"Erro ao gerar o placar: {e}")
#
#async def setup(bot):
#    await bot.add_cog(PintoGame(bot))

import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CommandError
import mysql.connector
from datetime import datetime, timedelta
import configparser
import os


# Caminho para o arquivo de configuração na pasta 'X9'
config_path = os.path.join('verde', 'db_config.ini')

# Lê o arquivo de configuração
config = configparser.ConfigParser()
config.read(config_path)

# Configuração do banco de dados
db_config = {
    'host': config['mysql']['host'],
    'user': config['mysql']['user'],
    'password': config['mysql']['password'],
    'database': config['mysql']['database']
}

# Conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Criação da tabela se não existir
def create_table_if_not_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pinto_scores (
            date DATE,
            server_id BIGINT,
            user_id BIGINT,
            username VARCHAR(255),
            size INT,
            PRIMARY KEY (date, user_id)
        )
    ''')
    conn.commit()
    conn.close()

class SortearPinto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        create_table_if_not_exists()
        self.duelo_cooldown = {}



    async def cog_check(self, ctx):
        return isinstance(ctx.channel, discord.TextChannel)

    @commands.hybrid_command(with_app_command=True, help='Sorteia um tamanho de pinto pra você.')
    async def pinto(self, ctx: commands.Context):
        user_id = ctx.author.id
        server_id = ctx.guild.id
        today = datetime.now().date()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT size FROM pinto_scores WHERE date = %s AND user_id = %s AND server_id = %s', (today, user_id, server_id))
        result = cursor.fetchone()

        if result:
            await ctx.send(f"{ctx.author.mention}, você já sorteou o pinto hoje!")
            conn.close()
            return

        numero_sorteado = random.randint(1, 50)
        embed = discord.Embed(title=f"{ctx.author.display_name} tem", description=f"# {numero_sorteado} cm de pau.", color=0x0000FF)
        embed.set_image(url='https://opresenterural.com.br/wp-content/uploads/2019/05/pintinho2-e1558016678542.jpg')
        if numero_sorteado <= 2:
            mensagem ="Uma clitóris avantajada!?";
        elif numero_sorteado <= 13:
            mensagem ="Pequetuxo.";
        elif numero_sorteado <= 20:
            mensagem ="Está na média.";
        elif numero_sorteado <= 30:
            mensagem ="O dote!";
        else:
            mensagem ="Caramba! Como cabe isso na calça?";

        embed.set_footer(text=mensagem)
        embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
        await ctx.send(embed=embed)

        # Atualizar o banco de dados
        cursor.execute('REPLACE INTO pinto_scores (date, server_id, user_id, username, size) VALUES (%s, %s, %s, %s, %s)',
                       (today, server_id, user_id, ctx.author.display_name, numero_sorteado))
        conn.commit()
        conn.close()

    @commands.hybrid_command(with_app_command=True, help='Desafie outro usuário para um duelo de pinto.')
    async def pinto_duelar(self, ctx: commands.Context, desafiante: discord.User):
        user_id = ctx.author.id
        server_id = ctx.guild.id
        desafiante_id = desafiante.id
        today = datetime.now().date()
        now = datetime.now()

        # Cooldown do duelo
        if user_id in self.duelo_cooldown and now < self.duelo_cooldown[user_id]:
            # Calcula a diferença de tempo restante
            tempo_restante = self.duelo_cooldown[user_id] - now
            minutos, segundos = divmod(int(tempo_restante.total_seconds()), 60)
            await ctx.send(f"Você deve esperar antes de desafiar novamente. Tempo restante: {minutos} minutos", ephemeral=True)
            return

        # Cooldown de 10 minutos
        self.duelo_cooldown[user_id] = now + timedelta(minutes=10)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o desafiante já sorteou o pinto
        cursor.execute('SELECT size FROM pinto_scores WHERE date = %s AND user_id = %s AND server_id = %s', (today, desafiante_id, server_id))
        desafiante_result = cursor.fetchone()
        if not desafiante_result:
            await ctx.send(f"{desafiante.mention}, você precisa sortear o pinto antes de ser desafiado!")
            conn.close()
            return

        # Verifica se o usuário atual já sorteou o pinto
        cursor.execute('SELECT size FROM pinto_scores WHERE date = %s AND user_id = %s AND server_id = %s', (today, user_id, server_id))
        result = cursor.fetchone()
        if not result:
            await ctx.send(f"{ctx.author.mention}, você precisa sortear o pinto antes de desafiar alguém!", ephemeral=True)
            conn.close()
            return
        
        desafiante_result = desafiante_result[0]
        result = result[0]

        # Verifica se o desafiante tem o pinto válido

        if desafiante_result == 0:
            await ctx.send(f"{ctx.author.mention}, você não pode desafiar uma mulher. Tente outra pessoa.")
            conn.close()
            return

        # Verifica se o usuário atual tem o pinto válido

        if result == 0 :
            await ctx.send(f"{desafiante.mention}, você virou mulher, não pode desafiar mais hoje porque não tem mais pinto. Espere até amanhã!")
            conn.close()
            return

        # Desafio
        bonus1=random.randint(1,20)
        bonus2=random.randint(1,20)

        tamanho_user = result + bonus1
        tamanho_desafiante = desafiante_result + bonus2

        bonustexto = f"{ctx.author.mention} ganhou mais {bonus1} cm de excitação, ficando com {tamanho_user} cm de pau!\n## {desafiante.mention} ganhou mais {bonus2} cm de excitação, ficando com {tamanho_desafiante} cm de pau!\n"


        if tamanho_user > tamanho_desafiante:
            novo_tamanho_user = result + 1
            novo_tamanho_desafiante = desafiante_result - 1
            resultado = f"{ctx.author.mention} venceu o duelo contra {desafiante.mention} e roubou 1 cm de pau!"
        elif tamanho_user < tamanho_desafiante:
            novo_tamanho_user = result - 1
            novo_tamanho_desafiante = desafiante_result + 1
            resultado = f"{desafiante.mention} venceu o duelo contra {ctx.author.mention} e roubou 1 cm de pau!"
        else:
            novo_tamanho_user = result
            novo_tamanho_desafiante = desafiante_result
            resultado = "O duelo terminou em empate!"


        # Verificação se o tamanho chegou a 0
        if novo_tamanho_user == 0:
            resultado += f"\n{ctx.author.mention} ficou sem pinto e virou mulher, por isso não pode mais duelar! Aguarde até amanhã."
        if novo_tamanho_desafiante == 0:
            resultado += f"\n{desafiante.mention} ficou sem pinto e virou mulher, por isso não pode mais duelar! Aguarde até amanhã."
        
        # Atualizar o banco de dados
        cursor.execute('UPDATE pinto_scores SET size = %s WHERE date = %s AND user_id = %s AND server_id = %s',
                        (novo_tamanho_user, today, user_id, server_id))
        cursor.execute('UPDATE pinto_scores SET size = %s WHERE date = %s AND user_id = %s AND server_id = %s',
                        (novo_tamanho_desafiante, today, desafiante_id, server_id))
        

        #cursor.execute('REPLACE INTO pinto_scores (date, server_id, user_id, username, size) VALUES (%s, %s, %s, %s, %s)',
        #               (today, server_id, user_id, ctx.author.display_name, novo_tamanho_user))
        #cursor.execute('REPLACE INTO pinto_scores (date, server_id, user_id, username, size) VALUES (%s, %s, %s, %s, %s)',
        #               (today, server_id, desafiante_id, desafiante.display_name, novo_tamanho_desafiante))
        conn.commit()
        conn.close()
        embed = discord.Embed(title="Resultado do duelo:", description=f"## {bonustexto}\n\n# {resultado}", color=discord.Color(random.randint(0, 0xFFFFFF)))
        embed.set_image(url="https://i.ibb.co/N9N2KWn/00000.jpg")
        await ctx.send(embed=embed)

    @commands.hybrid_command(with_app_command=True, help='Mostre o placar do pinto.')
    @app_commands.describe(date="A data no formato dd/mm/yyyy ou 'hoje' para o placar de hoje.")
    async def pinto_placar(self, ctx: commands.Context, date='hoje'):
        server_id = ctx.guild.id

        if date == 'hoje':
            # Pegar a data de hoje
            today = datetime.now().date()
            texto = "está passando a banana em todo mundo!"
        else:
            # Tentativa de conversão da data fornecida no formato dd/mm/yyyy
            try:
                today = datetime.strptime(date, "%d/%m/%Y").date()  # Converte para objeto date
                texto = 'passou a banana em todo mundo!'
            except ValueError:
                await ctx.send("Formato de data inválido. Use o formato dd/mm/yyyy.", ephemeral=True)
                return

        # Formatar a data para o formato usado no banco de dados (yyyy-mm-dd)
        formatted_db_date = today.strftime("%Y-%m-%d")
        formatted_display_date = today.strftime("%d/%m/%Y")  # Para exibir no embed

        conn = get_db_connection()
        cursor = conn.cursor()

        # Consulta ao banco usando a data formatada
        cursor.execute('SELECT user_id, username, size FROM pinto_scores WHERE date = %s AND server_id = %s ORDER BY size DESC', (formatted_db_date, server_id))
        result = cursor.fetchall()
        conn.close()

        if not result:
            await ctx.send(f"Ainda não há nenhum placar disponível para {formatted_display_date}.", ephemeral=True)
            return

        # Construir o embed
        embed = discord.Embed(title=f"Placar de Pintos da data de {formatted_display_date}", color=0x00FF00)
        for idx, (user_id, username, size) in enumerate(result, start=1):
            if idx == 1:
                username = f"👑 {username}"  # Adiciona o emoji de coroa ao primeiro lugar
                embed.set_footer(text=f"{username} {texto}")
            elif size == 0:
                username = f"👧🏻 {username}"  # Adiciona o emoji de garota ao pinto zero

            embed.add_field(name=f"#{idx} {username}", value=f"{size} cm", inline=False)

        embed.set_image(url="https://thumbs.dreamstime.com/b/cute-chick-cartoon-vector-illustration-58006002.jpg")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SortearPinto(bot))

