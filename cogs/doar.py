import discord
from discord.ext import commands

class Doacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="doar",help='Exibe um qrcode para transferência via pix para doações e apoio ao desenvolvedor do bot.')
    async def doar(self, ctx):
        imagem="qrcode.png"
        imagem_arquivo = discord.File(imagem)
        mensagem = "Para doar para o desenvolvedor, utilize o QR Code abaixo:"
        
        # Crie um objeto Embed para a mensagem
        embed = discord.Embed()
        embed.set_image(url=f"attachment://{imagem}")
    
        # Envie a mensagem com a imagem
        await ctx.send(mensagem)
        await ctx.send(embed=embed, file=imagem_arquivo)
        await ctx.send("Se quiser falar com o desenvolvedor, manda um zap pra ele que ele responde assim que puder: https://wa.me/5512981283235")
        


async def setup(bot):
    await bot.add_cog(Doacao(bot))        