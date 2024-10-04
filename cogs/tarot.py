import discord
from discord.ext import commands
import random
import pandas as pd
import os


class TarotBot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tarot_df = pd.read_excel('Tarot/tarot.xlsx', skiprows=0)
        self.image_path = os.path.dirname('Tarot') # caminho para a pasta onde está o script
        
    @commands.hybrid_command(with_app_command=True, help="Sorteia uma carta de Tarot para você")
    async def tarot(self,ctx: commands.Context):
        card = self.tarot_df.sample()
        nome = card.iloc[0, 0].title()
        normal = card.iloc[0, 1]
        invertido = card.iloc[0, 2]
        imagemnormal = card.iloc[0, 3]
        imageminvertida = card.iloc[0, 4]
        
        normal_ou_invertido = random.choice(['normal', 'invertido'])
        if normal_ou_invertido == 'normal':
            significado = f'Significado: {normal}.'
            imagem_url = imagemnormal
        else:
            significado = f'Significado (reverso): {invertido}.'
            imagem_url = imageminvertida # imagem de carta de cabeça para baixo
            
        embed = discord.Embed(title=f'Carta sorteada: {nome}', description=significado, color=discord.Color(random.randint(0, 0xFFFFFF)))
        embed.set_image(url=imagem_url)
        embed.set_footer(text=f"Sorteado por {ctx.author.display_name} ☪️☯️🕉️☸️✡️🔯🕎")
        embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
        message = await ctx.send(embed=embed)


        
async def setup(bot):
    await bot.add_cog(TarotBot(bot))

#import discord
#from discord.ext import commands
#import random
#import os
#import requests
#
#class TarotBot(commands.Cog):
#    def __init__(self, bot: commands.Bot):
#        self.bot = bot
#        self.tarot_data = self.load_tarot_data('Tarot/tarot.txt')  # Carregar o arquivo txt
#        self.image_path = os.path.dirname('Tarot')  # Caminho para a pasta onde está o script
#
#    def load_tarot_data(self, file_path):
#        tarot_data = []
#        with open(file_path, 'r', encoding='utf-8') as f:
#            lines = f.readlines()
#            for line in lines:
#                parts = line.strip().split('+')  # Separar as partes pelo '+'
#                if len(parts) == 5:  # Verificar se tem todos os dados (nome, normal, invertido, imagem normal, imagem invertida)
#                    card = {
#                        'nome': parts[0],
#                        'normal': parts[1],
#                        'invertido': parts[2],
#                        'imagemnormal': parts[3],
#                        'imageminvertida': parts[4]
#                    }
#                    tarot_data.append(card)
#        return tarot_data
#
#    def is_valid_image(self, url):
#        try:
#            response = requests.get(url)
#            return response.status_code == 200
#        except:
#            return False
#
#    @commands.hybrid_command(with_app_command=True, help="Sorteia uma carta de Tarot para você")
#    async def tarot(self, ctx: commands.Context):
#        card = random.choice(self.tarot_data)  # Escolher uma carta aleatoriamente
#        nome = card['nome'].title()
#        normal = card['normal']
#        invertido = card['invertido']
#        imagemnormal = card['imagemnormal']
#        imageminvertida = card['imageminvertida']
#
#        # Escolher se será a carta normal ou invertida
#        normal_ou_invertido = random.choice(['normal', 'invertido'])
#        if normal_ou_invertido == 'normal':
#            significado = f'Significado: {normal}.'
#            imagem_url = imagemnormal
#        else:
#            significado = f'Significado (reverso): {invertido}.'
#            imagem_url = imageminvertida
#
#        embed = discord.Embed(
#            title=f'Carta sorteada: {nome}', 
#            description=significado, 
#            color=discord.Color(random.randint(0, 0xFFFFFF))
#        )
#        
#        # Verificar se a imagem é válida antes de exibir
#        if self.is_valid_image(imagem_url):
#            embed.set_image(url=imagem_url)
#        else:
#            embed.set_image(url='https://c8.alamy.com/comp/2RPHFC5/tarot-card-back-design-mystical-esoteric-symbols-2RPHFC5.jpg')  # Imagem padrão se a URL for inválida
#
#        embed.set_footer(text=f"Sorteado por {ctx.author.display_name} ☪️☯️🕉️☸️✡️🔯🕎")
#        embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
#        
#        message = await ctx.send(embed=embed)
#
#async def setup(bot):
#    await bot.add_cog(TarotBot(bot))
