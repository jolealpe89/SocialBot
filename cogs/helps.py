from discord.ext import commands
import discord
import os
import random
import asyncio
prefixo = os.environ.get('PREFIXO')
prefixo=',a'

class Ajudas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.classname = 'Ajuda'        
 
    #@commands.command(name="help", aliases=['ajuda'], help="Comando de ajuda que mostra todos os comandos do bot e suas alternativas de uso.")
    async def helpe_command(self, ctx):
        helptxt = {}
        for command in self.bot.commands:
            classname = command.cog_name
            if classname not in helptxt:
                helptxt[classname] = ''
            helptxt[classname] += f'**{command}** \n **Descrição:** {command.help}  \n **Alternativas** `{", ".join(command.aliases)}`\n \n'
    
        # Envia uma mensagem embed para cada classe
        for classname, classhelp in helptxt.items():
            parts = divide_texto(classhelp, 1500)
            for i, part in enumerate(parts):
                embedhelp = discord.Embed(
                    color=discord.Color(random.randint(0, 0xFFFFFF)),
                    title=f'Comandos do módulo `{classname}` da {self.bot.user.name}\nUtilize o prefixo `{prefixo}`\n \n',
                    description=part
                )
                embedhelp.set_thumbnail(url=self.bot.user.avatar.url)
                if i == 0:
                    # Se for a primeira parte, adiciona o link para a segunda parte
                    embedhelp.description += f'\n (Utilize `{prefixo}help` para ver os comandos)'
                await ctx.send(embed=embedhelp)

    @commands.command(name="help", aliases=['ajuda'], help="Comando de ajuda que mostra todos os comandos do bot e suas alternativas de uso.")
    async def help_command(self, ctx):
        helptxt = {}
        for command in self.bot.commands:
            classname = command.cog_name
            if classname not in helptxt:
                helptxt[classname] = ''
            helptxt[classname] += f'**{command}** \n **Descrição:** {command.help}  \n **Alternativas** `{", ".join(command.aliases)}`\n \n'
    
        # Combina todas as partes em uma mensagem
        all_parts = []
        for classname, classhelp in helptxt.items():
            parts = divide_texto(classhelp, 1500)
            for i, part in enumerate(parts):
                embedhelp = discord.Embed(
                    color=discord.Color(random.randint(0, 0xFFFFFF)),
                    title=f'Comandos do módulo `{classname}` da {self.bot.user.name}\nUtilize o prefixo `{prefixo}`\n \n',
                    description=part
                )
                embedhelp.set_thumbnail(url=self.bot.user.avatar.url)
                if i == 0:
                    # Se for a primeira parte, adiciona o link para a segunda parte
                    embedhelp.description += f'\n (Utilize `{prefixo}help` para ver os comandos)'
                all_parts.append(embedhelp)
    
        # Verifica se a mensagem foi enviada em um canal privado
        if isinstance(ctx.channel, discord.DMChannel):
            # Envia a mensagem de ajuda diretamente para o autor da mensagem
            await self.helpe_command(ctx)

        else:
            # Envia a mensagem de ajuda no canal em que a mensagem foi recebida
            current_page = 0
            message = await ctx.send(embed=all_parts[current_page])
            await message.add_reaction('⬅️')
            await message.add_reaction('➡️')
    
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']
    
        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                if not isinstance(ctx.channel, discord.DMChannel):
                    await message.clear_reactions()
                break
            else:
                if str(reaction.emoji) == '➡️' and current_page < len(all_parts)-1:
                    current_page += 1
                    await message.edit(embed=all_parts[current_page])
                elif str(reaction.emoji) == '⬅️' and current_page > 0:
                    current_page -= 1
                    await message.edit(embed=all_parts[current_page])
                await message.remove_reaction(reaction, user)

                
                
def divide_texto(texto, max_chars):
    """Divide um texto em várias partes, cada uma com no máximo max_chars caracteres."""
    parts = []
    current_part = ''
    for line in texto.splitlines():
        if len(current_part) + len(line) + 1 > max_chars:
            # Se a próxima linha não couber nesta parte, adiciona a parte atual à lista de partes e começa uma nova parte
            parts.append(current_part)
            current_part = ''
        current_part += line + '\n'
    if current_part:
        # Adiciona a última parte à lista de partes
        parts.append(current_part)
    return parts
    
async def setup(bot):
    await bot.add_cog(Ajudas(bot))