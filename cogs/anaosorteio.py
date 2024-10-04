import discord
from discord.ext import commands
import random
import os
from discord import app_commands

class DwarfCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.hybrid_command(with_app_command=True, help='Sorteia um anão pra você.')
    async def anao(self, ctx:commands.Context):
        # Caminho do arquivo e da pasta
        file_path = 'Dwarf/anao.txt'

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                chosen_line = random.choice(lines).strip()
                name, value, image_file = chosen_line.split('-')

                embed = discord.Embed(
                    title="**Sorteio de Anão**",
                    description=f"# {name}\n## Valor: {value}",
                    color=discord.Color.blue()
                )

                embed.set_image(url=f"{image_file}")
                embed.set_footer(text=f'Anão sorteado por {ctx.author.display_name}')
                embed.set_thumbnail(url=f'{ctx.author.display_avatar}')

                await ctx.send(embed=embed)

        except FileNotFoundError:
            await ctx.send("O arquivo anao.txt não foi encontrado na pasta Dwarf.")
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {str(e)}")







async def setup(bot):
    await bot.add_cog(DwarfCog(bot))