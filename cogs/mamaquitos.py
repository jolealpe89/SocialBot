import discord
from discord.ext import commands
import random

class MacacoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(with_app_command=True, help='Sorteia um macaco pra você.')
    async def macaco(self, ctx: commands.Context):
        with open('Macacos/mamacos.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            macacos = []
            current_macaco = []
            for line in lines:
                if line.strip() == "":
                    macacos.append(current_macaco)
                    current_macaco = []
                else:
                    current_macaco.append(line.strip())

            # Randomly select a macaco
            selected_macaco = random.choice(macacos)

            embed = discord.Embed(title="Você é um:", description=selected_macaco[0], color=0x00ff00)
            embed.add_field(name="Características", value=selected_macaco[1], inline=False)
            embed.add_field(name="Habitat", value=selected_macaco[2], inline=False)
            embed.set_image(url=selected_macaco[3])
            embed.set_footer(text=f"{ctx.author.display_name} é este macaco.")
            embed.set_thumbnail(url=f'{ctx.author.display_avatar}')

            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MacacoCog(bot))
