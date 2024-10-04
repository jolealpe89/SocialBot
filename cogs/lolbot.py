#import discord
#from discord.ext import commands
#import random
#import requests
#from bs4 import BeautifulSoup
#
#class LeagueBot(commands.Cog):
#    def __init__(self, bot: commands.Bot):
#        self.bot = bot
#
#    async def sortear_champion(self, category):
#        try:
#            with open(f'BotLoL/{category}.txt', 'r', encoding='utf-8') as f:
#                champion = random.choice(f.readlines()).strip().lower()
#            return champion
#        except Exception as e:
#            raise commands.CommandError(f"Erro ao sortear campeão: {e}")
#
#    async def sortear_item(self):
#        try:
#            with open('BotLoL/itens.txt', 'r', encoding='utf-8') as f:
#                item = random.choice(f.readlines()).strip()
#            return item
#        except Exception as e:
#            raise commands.CommandError(f"Erro ao sortear item: {e}")
#
#    async def generate_champion_embed(self, ctx:commands.Context, champion):
#        try:
#            response_detalhes = requests.get(f"https://www.leagueoflegends.com/pt-br/champions/{champion}/")
#            soup_detalhes = BeautifulSoup(response_detalhes.text, 'html.parser')
#
#            descricao_campeao_elemento = soup_detalhes.find('p', {'data-testid': 'overview:description'})
#            descricao_campeao = descricao_campeao_elemento.get_text(separator='\n') if descricao_campeao_elemento else "Descrição não disponível."
#
#            div_imagem_campeao_elemento = soup_detalhes.find('div', {'data-testid': 'overview:backgroundimage'})
#            img_imagem_campeao_elemento = div_imagem_campeao_elemento.find('img') if div_imagem_campeao_elemento else None
#            url_imagem_campeao = img_imagem_campeao_elemento['src'] if img_imagem_campeao_elemento and 'src' in img_imagem_campeao_elemento.attrs else "URL da imagem não disponível."
#
#            embed = discord.Embed(
#                title=f"{champion.capitalize()}",
#                description=f"{descricao_campeao}\n\n[Ver Página Completa](https://www.leagueoflegends.com/pt-br/champions/{champion}/)",
#                color=discord.Color(random.randint(0, 0xFFFFFF))
#            )
#            embed.set_image(url=url_imagem_campeao)
#            embed.set_footer(text=f"{ctx.author.display_name} ☪️☯️🕉️☸️✡️🔯🕎")
#            return embed
#        except Exception as e:
#            raise commands.CommandError(f"Erro ao gerar embed: {e}")
#
#    @commands.hybrid_command(with_app_command=True, name="sortearchampion", help="Sorteia um champ: champions, atiradores, assassinos, magos, tanques, suportes, lutadores")
#    async def sorteio_campeao(self, ctx:commands.Context, tipo:str):
#        try:
#            champion = await self.sortear_champion(tipo)
#            embed = await self.generate_champion_embed(ctx, champion)
#            await ctx.send(embed=embed)
#        except commands.CommandError as e:
#            await ctx.send(str(e))
#
#   
#
#    @commands.hybrid_command(with_app_command=True, name="mostrarchamp", help="Exibe um campeão do League of Legends.")
#    async def mostrar_champion(self, ctx:commands.Context, *, chanpinhon: str):
#        try:
#            embed = await self.generate_champion_embed(ctx, chanpinhon.lower())
#            await ctx.send(embed=embed)
#        except commands.CommandError as e:
#            await ctx.send(str(e))
#
#async def setup(bot):
#    await bot.add_cog(LeagueBot(bot))
import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError


class LeagueBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def sortear_champion(self, category):
        try:
            with open(f'BotLoL/{category}.txt', 'r', encoding='utf-8') as f:
                champion = random.choice(f.readlines()).strip().lower()
            return champion
        except FileNotFoundError:
            raise commands.CommandError(f"Arquivo '{category}.txt' não encontrado.")
        except Exception as e:
            raise commands.CommandError(f"Erro ao sortear campeão: {e}")

    async def sortear_item(self):
        try:
            with open('BotLoL/itens.txt', 'r', encoding='utf-8') as f:
                item = random.choice(f.readlines()).strip()
            return item
        except FileNotFoundError:
            raise commands.CommandError("Arquivo 'itens.txt' não encontrado.")
        except Exception as e:
            raise commands.CommandError(f"Erro ao sortear item: {e}")

    async def generate_champion_embed(self, ctx: commands.Context, champion):
        try:
            # Verifica se o nome do campeão está formatado corretamente
            champion_name = champion.replace(" ", "-").lower()
            response_detalhes = requests.get(f"https://www.leagueoflegends.com/pt-br/champions/{champion_name}/")
            response_detalhes.raise_for_status()  # Verifica se a chamada foi bem-sucedida
            soup_detalhes = BeautifulSoup(response_detalhes.text, 'html.parser')

            #descricao_campeao_elemento = soup_detalhes.find('p', {'data-testid': 'overview:description'})
            descricao_campeao_elemento = soup_detalhes.find('div', {'data-testid': 'rich-text-html'})
            descricao_campeao = descricao_campeao_elemento.get_text(separator='\n') if descricao_campeao_elemento else "Descrição não disponível."

            #div_imagem_campeao_elemento = soup_detalhes.find('div', {'data-testid': 'overview:backgroundimage'})
            #img_imagem_campeao_elemento = div_imagem_campeao_elemento.find('img') if div_imagem_campeao_elemento else None
            #url_imagem_campeao = img_imagem_campeao_elemento['src'] if img_imagem_campeao_elemento and 'src' in img_imagem_campeao_elemento.attrs else "URL da imagem não disponível."
            div_imagem_campeao_elemento = soup_detalhes.find('div', {'data-testid': 'backdrop-background'})
            img_imagem_campeao_elemento = div_imagem_campeao_elemento.find('img') if div_imagem_campeao_elemento else None
            url_imagem_campeao = img_imagem_campeao_elemento['src'] if img_imagem_campeao_elemento and 'src' in img_imagem_campeao_elemento.attrs else "URL da imagem não disponível."

            embed = discord.Embed(
                title=f'# {champion.capitalize()}',
                description=f'{descricao_campeao}\n\n[Ver Página Completa](https://www.leagueoflegends.com/pt-br/champions/{champion_name}/)',
                color=discord.Color(random.randint(0, 0xFFFFFF))
            )
            embed.set_image(url=url_imagem_campeao)
            embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
            embed.set_footer(text=f'Sorteio realizado por **{ctx.author.display_name}**')
            return embed
        except ConnectionError:
            raise commands.CommandError("Erro de conexão ao acessar a página do campeão. Verifique sua conexão de internet.")
        except requests.HTTPError as e:
            raise commands.CommandError(f"Erro HTTP ao acessar a página do campeão: {e}")
        except Exception as e:
            raise commands.CommandError(f"Erro ao gerar embed: {e}")

    @commands.hybrid_command(with_app_command=True, name="sortearchampion", help="Sorteia um champ: champion, atirador, assassino, mago, tanque, suporte, lutador")
    async def sorteio_campeao(self, ctx: commands.Context, tipo: str = 'champion'):
        await ctx.send('Ok!')

        try:
            champion = await self.sortear_champion(tipo)
            embed = await self.generate_champion_embed(ctx, champion)
            await ctx.send(embed=embed)
        except commands.CommandError as e:
            await ctx.send(str(e))

    @commands.hybrid_command(with_app_command=True, name="mostrarchamp", help="Exibe um campeão do League of Legends.")
    async def mostrar_champion(self, ctx: commands.Context, *, chanpinhon: str):
        try:
            embed = await self.generate_champion_embed(ctx, chanpinhon.lower())
            await ctx.send(embed=embed)
        except commands.CommandError as e:
            await ctx.send(str(e))


async def setup(bot):
    await bot.add_cog(LeagueBot(bot))
