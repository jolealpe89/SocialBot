import discord
from discord.ext import commands

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites = {}

    # Armazenar convites ao iniciar o bot
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.invites[guild.id] = await guild.invites()

    # Função que verifica por qual convite o usuário entrou
    async def check_invite(self, member):
        guild_invites = await member.guild.invites()
        old_invites = self.invites.get(member.guild.id, [])

        used_invite = None

        # Comparar convites anteriores com os atuais
        for old_invite in old_invites:
            for current_invite in guild_invites:
                if old_invite.code == current_invite.code and old_invite.uses < current_invite.uses:
                    used_invite = current_invite
                    break

        # Atualizar o dicionário de convites
        self.invites[member.guild.id] = guild_invites

        return used_invite

    # Comando que recebe um usuário e verifica qual convite ele usou
    @commands.hybrid_command(with_app_command=True)
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def check_invite_member(self, ctx:commands.Context, member: discord.Member):
        invite = await self.check_invite(member)
        if invite:
            await ctx.send(f"{member.mention} {member.id} entrou usando o convite {invite.code}, criado por {invite.inviter.mention}.", ephemeral=True)
        else:
            await ctx.send(f"Não foi possível identificar o convite usado por {member.mention}.", ephemeral=True)

# Adicionar a Cog ao bot
async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
