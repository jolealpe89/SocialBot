import os
import datetime
from discord.ext import commands
import asyncio
prefixo = ",b"
class Avaliador(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_file_structure(self, guild_id):
        # Criar diretório da classe
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)

        # Criar diretório do servidor se não existir
        server_dir = os.path.join(class_dir, str(guild_id))
        if not os.path.exists(server_dir):
            os.makedirs(server_dir)

        # Criar o arquivo sugestoes.txt se não existir
        sugestoes_file = os.path.join(server_dir, 'sugestoes.txt')
        if not os.path.exists(sugestoes_file):
            with open(sugestoes_file, 'w', encoding='utf-8') as file:
                pass


    @commands.command(name='comentar', help=f'Envia comentários anônimos para críticas e sugestões para melhorias do servidor. Você usa: `{prefixo}bavaliar <id_do_server> <seus_comentários>`. Ex.: `{prefixo}avaliar 14587415481251841 Gostaria que tivesse um canal para postar temas NSFW`', aliases=['avaliar','sugerir'])
    async def sugestao(self, ctx, server_id: int = 0, *, sugestao: str = None):
        guild_id = str(server_id)
        await self.create_file_structure(guild_id)       
        autor = ctx.author.name
        horario = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') 
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        directory = os.path.join(class_dir, guild_id)   
        with open(os.path.join(directory, 'sugestoes.txt'), 'a', encoding='utf-8') as f:
                #f.write(f'{autor}\nData/Hora: {horario}\n{sugestao}\n\n')
            f.write(f'Data/Hora: {horario}\n{sugestao}\n=========================================\n')
        await ctx.send('Sugestão salva com sucesso! Obrigado por sua colaboração.')

    @commands.command(name='feedback', help='Lê todos os comentários salvos no arquivo.')
    @commands.is_owner()
    async def ler_comentarios(self, ctx, server_id):
        guild_id = str(server_id)
        class_dir = os.path.join(os.getcwd(), type(self).__name__)
        directory = os.path.join(class_dir, guild_id)

        try:
            with open(os.path.join(directory, 'sugestoes.txt'), 'r', encoding='utf-8') as f:
                comentarios = f.readlines()
                if comentarios:
                    for comentario in comentarios:
                        await ctx.send(comentario.strip())
                else:
                    await ctx.send('Nenhum comentário encontrado.')
                    return
        except FileNotFoundError:
            await ctx.send('Nenhum comentário encontrado.')
            return
            

        # Pergunta se o usuário quer excluir todos os comentários
        await ctx.send('Deseja excluir todos os comentários? Responda com "sim" ou "não".')

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            resposta = await self.bot.wait_for('message', timeout=30, check=check)
            if resposta.content.lower() == 'sim':
                # Se o usuário responder "sim", você pode adicionar o código para excluir os comentários aqui
                with open(os.path.join(directory, 'sugestoes.txt'), 'w', encoding='utf-8') as f:
                    f.truncate(0)  # Limpa o arquivo
                await ctx.send('Todos os comentários foram excluídos.')
            else:
                await ctx.send('Nenhum comentário foi excluído.')

        except asyncio.TimeoutError:
            await ctx.send('Tempo esgotado. Nenhum comentário foi excluído.')
    @ler_comentarios.error
    async def excluir_todas_lojas_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            await ctx.send("Você não tem permissão para executar este comando.")


async def setup(bot):
    await bot.add_cog(Avaliador(bot))