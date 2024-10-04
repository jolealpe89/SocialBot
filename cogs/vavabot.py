#import discord
#from discord.ext import commands
#import random
#import requests
#from bs4 import BeautifulSoup
#from discord import app_commands
#
#class ValorantBot(commands.Cog):
#    def __init__(self, bot: commands.Bot):
#        self.bot = bot
#
#    async def sortear_agente(self):
#        with open('BotValorant/agentes.txt', 'r', encoding='utf-8') as f:
#            agente = random.choice(f.readlines()).strip().lower()
#        return agente
#    
#    @app_commands.command(name="sortearagente", description="Sorteia um agente aleatório de Valorant.")
#    async def sorteio_agente(self, interaction: discord.Interaction):
#        try:
#            agente = await self.sortear_agente()
#            agente_formatado =  '-'.join(part.capitalize() for part in agente.split('/'))
#
#            # Faz uma segunda requisição para obter informações detalhadas do campeão
#            response_detalhes = requests.get(f"https://playvalorant.com/pt-br/agents/{agente_formatado.lower()}/")
#            soup_detalhes = BeautifulSoup(response_detalhes.text, 'html.parser')
#
#            # Extrai a descrição do agente
#            descricao_agente_elemento = soup_detalhes.find('div', {'data-testid': 'rich-text-html'})
#            
#            if descricao_agente_elemento:
#                descricao_agente = descricao_agente_elemento.get_text(separator='\n')  # Separa as linhas do texto
#
#            else:
#                descricao_agente = "Descrição não disponível."
#
#
#            #Extrai a função do agente
#            funcao_agente_elemento = soup_detalhes.find('p', {'data-testid':'meta-details'})
#            if funcao_agente_elemento:
#                funcao_agente = funcao_agente_elemento.get_text(separator='\n')  # Separa as linhas do texto
#
#            else:
#                funcao_agente = "Descrição não disponível."
#
#
#
#            # Extrai a URL da imagem
#            img_imagem_agente_elemento = soup_detalhes.find('img', {'data-testid':'mediaImage'})
#            
#            if img_imagem_agente_elemento and 'src' in img_imagem_agente_elemento.attrs:
#                url_imagem_agente = img_imagem_agente_elemento['src']
#
#            else:
#                url_imagem_agente = "URL da imagem não disponível."
#
#            # Cria um embed com as informações do campeão
#            embed = discord.Embed(
#                title=f"Agente Sorteado:\n\n{agente.capitalize()}",
#                description=f"**Função: {funcao_agente}**\n\n{descricao_agente}",
#                color=discord.Color(random.randint(0, 0xFFFFFF))  # Cor aleatória
#            )
#            embed.set_image(url=url_imagem_agente)
#            embed.set_footer(text=f"Sorteado por {interaction.user.display_name} ☪️☯️🕉️☸️✡️🔯🕎")
#
#            # Envia o embed no canal do Discord
#            await interaction.response.send_message(embed=embed)
#
#        except Exception as e:
#            # Tratamento de exceções
#            await interaction.response.send_message(f"Ocorreu um erro: {e}")
#
#
#async def setup(bot:commands.Bot) -> None:
#    await bot.add_cog(ValorantBot(bot))

import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup
from discord import app_commands

class ValorantBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def sortear_agente(self):
        with open('BotValorant/agentes.txt', 'r', encoding='utf-8') as f:
            chosen_line = random.choice(f.readlines()).strip()
            agente, imagem = chosen_line.split(' , ')

        return agente , imagem
    
    @commands.hybrid_command(with_app_command=True, help="Sorteia um agente aleatório de Valorant.")
    async def agente(self, ctx: commands.Context):
        try:
            agente, imagem = await self.sortear_agente()
            agente_formatado =  '-'.join(part.capitalize() for part in agente.split('/'))

            # Faz uma requisição para obter informações detalhadas do agente
            response_detalhes = requests.get(f"https://playvalorant.com/pt-br/agents/{agente_formatado.lower()}/")
            soup_detalhes = BeautifulSoup(response_detalhes.text, 'html.parser')

            # Extrai a descrição do agente
            descricao_agente_elemento = soup_detalhes.find('div', class_='sc-4225abdc-0 lnNUuw')
            if descricao_agente_elemento:
                descricao_agente = descricao_agente_elemento.get_text(separator='\n')
            else:
                descricao_agente = "Descrição não disponível."

            # Extrai a função do agente
            funcao_agente_elemento = soup_detalhes.find('p', {'data-testid':'meta-details'})
            if funcao_agente_elemento:
                funcao_agente = funcao_agente_elemento.get_text(separator='\n')
            else:
                funcao_agente = "Função não disponível."

            # Extrai a URL da imagem
#            img_imagem_agente_elemento = soup_detalhes.find('div', {'data-testid':'backdrop-background'})
#            url_imagem_agente = None
#            if img_imagem_agente_elemento and 'src' in img_imagem_agente_elemento.attrs:
#                url_imagem_agente = img_imagem_agente_elemento['src']
#                print(f"URL da Imagem: {url_imagem_agente}") 
#                if not url_imagem_agente.startswith('http'):
#                    url_imagem_agente = 'https:' + url_imagem_agente
#
#                # Verifica se a URL é um data URL ou um SVG
#                if "data:image" in url_imagem_agente or ".svg" in url_imagem_agente:
#                    url_imagem_agente = None  # Invalida a URL se for um data URL ou SVG
#            
#            if not url_imagem_agente:
#                # Define uma imagem padrão se nenhuma imagem válida for encontrada
#                url_imagem_agente = "https://seeklogo.com/images/V/valorant-logo-FAB2CA0E55-seeklogo.com.png"  # Substitua por uma URL de imagem padrão válida
#
#            print(f"URL da Imagem: {url_imagem_agente}")  # Debug: Verifique a URL da imagem
#

#            div_imagem_agente_elemento = soup_detalhes.find('div', {'data-testid': 'backdrop-background'})
#            img_imagem_agente_elemento = div_imagem_agente_elemento.find('img') if div_imagem_agente_elemento else None
#            url_imagem_agente = img_imagem_agente_elemento['src'] if img_imagem_agente_elemento and 'src' in img_imagem_agente_elemento.attrs else "URL da imagem não disponível."
#
#            # Verificar se a URL não é uma SVG e se tem uma extensão de imagem válida
#            if url_imagem_agente.startswith("data:image/svg+xml"):
#                url_imagem_agente = "https://seeklogo.com/images/V/valorant-logo-FAB2CA0E55-seeklogo.com.png"
#            elif any(ext in url_imagem_agente for ext in [".png", ".jpg", ".jpeg", ".gif"]):
#                # Tratamento para remover tudo após a extensão da imagem
#                url_imagem_agente = url_imagem_agente.split("?")[0]
#
            #print(url_imagem_agente)
            # Cria um embed com as informações do agente
            embed = discord.Embed(
                title=f"Agente Sorteado: {agente.capitalize()}",
                description=f"**Função: {funcao_agente}**\n\n{descricao_agente}",
                color=discord.Color(random.randint(0, 0xFFFFFF))
            )
            embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
            embed.set_image(url=imagem)
#            
#            # Adiciona a imagem ao embed se a URL for válida
#            if url_imagem_agente:
#                embed.set_image(url=url_imagem_agente)
            
            embed.set_footer(text=f"Sorteado por {ctx.author.display_name}")

            # Envia o embed no canal do Discord
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}")

async def setup(bot):
    await bot.add_cog(ValorantBot(bot))

