#import discord
#from discord.ext import commands
#
#class MyBot(commands.Cog):
#    
#    def __init__(self, bot):
#        self.bot = bot
#        self.user_id = 269512782536245258
#
#    @commands.Cog.listener()
#    async def on_message(self, message):
#        if message.author.bot:
#            return False
#        if isinstance(message.channel, discord.DMChannel):
#            # O bot recebeu uma mensagem privada, vamos enviar uma mensagem privada para o usuário com ID 269512782536245258
#            user = await self.bot.fetch_user(269512782536245258)
#            
#            # Verifica se o autor da mensagem é diferente do usuário 'user'
#            if message.author.id != user.id:
#                content = f"**{message.author}**\n **ID:** {message.author.id} enviou a seguinte mensagem:\n\n{message.content}"
#                
#                if message.attachments:
#                    attachments = [attachment.url for attachment in message.attachments]
#                    content += "\nAnexos: " + ", ".join(attachments)
#                
#                await user.send(content)
#
#
#                
#async def setup(bot):
#    await bot.add_cog(MyBot(bot))
import discord
from discord.ext import commands
import os

class MyBot(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.user_ids = self.load_user_ids()

    def load_user_ids(self):
        file_path = os.path.join("Polvinho", "user_ids.txt")
        try:
            with open(file_path, "r") as file:
                return [int(line.strip()) for line in file if line.strip().isdigit()]
        except FileNotFoundError:
            print(f"Arquivo {file_path} não encontrado.")
            return []

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return False
        if isinstance(message.channel, discord.DMChannel):
            for user_id in self.user_ids:
                user = await self.bot.fetch_user(user_id)
                if message.author.id != user.id:
                    content = f"**{message.author}**\n **ID:** {message.author.id} enviou a seguinte mensagem:\n\n{message.content}"
                    
                    if message.attachments:
                        attachments = [attachment.url for attachment in message.attachments]
                        content += "\nAnexos: " + ", ".join(attachments)
                    
                    await user.send(content)

    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def dm_all_members(self, ctx, guild_id: int, message: str):
        guild = self.bot.get_guild(guild_id)
        if not guild:
            await ctx.send("Servidor não encontrado.")
            return
        
        for member in guild.members:
            if member.bot:
                continue  # Ignora bots
            try:
                await member.send(message)
                print(f"Mensagem enviada para {member.name}#{member.discriminator}")
            except discord.Forbidden:
                print(f"Não foi possível enviar mensagem para {member.name}#{member.discriminator}")
        
        await ctx.send("Mensagem enviada para todos os membros!")

async def setup(bot):
    await bot.add_cog(MyBot(bot))
