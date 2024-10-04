from discord.ext import commands, tasks
import random
import discord
from datetime import datetime, timedelta

class DwarfMarket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dwarves = {}  # Armazena os anões dos usuários
        self.market = []  # Anões disponíveis no mercado
        self.balances = {}  # Saldo de cada jogador
        self.wild_dwarves = []  # Anões selvagens
        self.last_market_update = datetime.now()
        self.update_market.start()  # Inicia o ciclo de atualização do mercado a cada 3 horas

    # Função auxiliar para gerar um anão aleatório
    def generate_dwarf(self):
        names = ["Thorin", "Balin", "Dwalin", "Gloin", "Bifur", "Bofur", "Bombur"]
        strength = random.randint(1, 100)
        intelligence = random.randint(1, 100)
        agility = random.randint(1, 100)
        value = (strength + intelligence + agility) * 10
        return {
            "name": random.choice(names),
            "strength": strength,
            "intelligence": intelligence,
            "agility": agility,
            "value": value
        }

    # Atualiza o mercado a cada 3 horas
    @tasks.loop(hours=3)
    async def update_market(self):
        self.market = [self.generate_dwarf() for _ in range(5)]
        self.last_market_update = datetime.now()

    @commands.hybrid_command(with_app_command=True)
    async def sortear_anao(self, ctx:commands.Context):
        """Sorteia um anão com atributos e adiciona à conta do jogador."""
        dwarf = self.generate_dwarf()

        if ctx.author.id not in self.dwarves:
            self.dwarves[ctx.author.id] = []
        self.dwarves[ctx.author.id].append(dwarf)

        if ctx.author.id not in self.balances:
            self.balances[ctx.author.id] = 100

        await ctx.send(f"Você sorteou um anão! Nome: {dwarf['name']}, Força: {dwarf['strength']}, "
                       f"Inteligência: {dwarf['intelligence']}, Agilidade: {dwarf['agility']}, "
                       f"Valor: {dwarf['value']} moedas.")

    @commands.hybrid_command(with_app_command=True)
    async def meus_anoes(self, ctx:commands.Context):
        """Mostra a lista de anões do jogador."""
        if ctx.author.id not in self.dwarves or not self.dwarves[ctx.author.id]:
            await ctx.send(f"Você não tem nenhum anão, {ctx.author.mention}. Use `!sortear_anao`.")
        else:
            anoes = self.dwarves[ctx.author.id]
            msg = f"Seus anões, {ctx.author.mention}:\n"
            for idx, dwarf in enumerate(anoes, 1):
                msg += f"{idx}. {dwarf['name']} - Força: {dwarf['strength']}, Inteligência: {dwarf['intelligence']}, Agilidade: {dwarf['agility']}, Valor: {dwarf['value']} moedas\n"
            await ctx.send(msg)

    @commands.hybrid_command(with_app_command=True)
    async def vender_anao(self, ctx:commands.Context, dwarf_index: int):
        """Vende um anão para o mercado."""
        if ctx.author.id not in self.dwarves or dwarf_index <= 0 or dwarf_index > len(self.dwarves[ctx.author.id]):
            await ctx.send(f"Anão inválido, {ctx.author.mention}. Verifique sua lista com `!meus_anoes`.")
            return

        dwarf = self.dwarves[ctx.author.id].pop(dwarf_index - 1)
        self.market.append(dwarf)
        self.balances[ctx.author.id] += dwarf["value"]

        await ctx.send(f"Você vendeu o anão {dwarf['name']} por {dwarf['value']} moedas. Saldo: {self.balances[ctx.author.id]} moedas.")

    @commands.hybrid_command(with_app_command=True)
    async def comprar_anao(self, ctx:commands.Context, dwarf_index: int):
        """Compra um anão do mercado."""
        if dwarf_index <= 0 or dwarf_index > len(self.market):
            await ctx.send(f"Anão inválido no mercado, {ctx.author.mention}. Use `!mercado` para verificar o mercado.")
            return

        dwarf = self.market[dwarf_index - 1]

        if ctx.author.id not in self.balances or self.balances[ctx.author.id] < dwarf["value"]:
            await ctx.send(f"Você não tem moedas suficientes, {ctx.author.mention}.")
            return

        self.market.pop(dwarf_index - 1)
        self.dwarves[ctx.author.id].append(dwarf)
        self.balances[ctx.author.id] -= dwarf["value"]

        await ctx.send(f"Você comprou o anão {dwarf['name']} por {dwarf['value']} moedas. Saldo: {self.balances[ctx.author.id]} moedas.")

    @commands.hybrid_command(with_app_command=True)
    async def mercado(self, ctx:commands.Context):
        """Mostra os anões disponíveis no mercado."""
        if not self.market:
            await ctx.send("O mercado está vazio.")
        else:
            msg = "Anões no mercado:\n"
            for idx, dwarf in enumerate(self.market, 1):
                msg += f"{idx}. {dwarf['name']} - Força: {dwarf['strength']}, Inteligência: {dwarf['intelligence']}, Agilidade: {dwarf['agility']}, Valor: {dwarf['value']} moedas\n"
            await ctx.send(msg)

    @commands.hybrid_command(with_app_command=True)
    async def saldo(self, ctx:commands.Context):
        """Mostra o saldo de moedas do jogador."""
        saldo = self.balances.get(ctx.author.id, 100)
        await ctx.send(f"Seu saldo: {saldo} moedas, {ctx.author.mention}.")

    @commands.hybrid_command(with_app_command=True)
    async def batalha_anoes(self, ctx:commands.Context, user: discord.User, dwarf_index: int, opponent_dwarf_index: int):
        """Batalha de anões entre dois jogadores."""
        if ctx.author.id not in self.dwarves or dwarf_index <= 0 or dwarf_index > len(self.dwarves[ctx.author.id]):
            await ctx.send(f"Anão inválido, {ctx.author.mention}. Verifique sua lista com `!meus_anoes`.")
            return

        if user.id not in self.dwarves or opponent_dwarf_index <= 0 or opponent_dwarf_index > len(self.dwarves[user.id]):
            await ctx.send(f"O jogador {user.mention} não tem um anão válido.")
            return

        dwarf_user = self.dwarves[ctx.author.id][dwarf_index - 1]
        dwarf_opponent = self.dwarves[user.id][opponent_dwarf_index - 1]

        # Sistema de batalha baseado na soma dos atributos
        user_score = dwarf_user["strength"] + dwarf_user["intelligence"] + dwarf_user["agility"]
        opponent_score = dwarf_opponent["strength"] + dwarf_opponent["intelligence"] + dwarf_opponent["agility"]

        if user_score > opponent_score:
            self.dwarves[ctx.author.id].append(dwarf_opponent.copy())  # Jogador vence e ganha uma cópia do anão do adversário
            await ctx.send(f"{ctx.author.mention} venceu a batalha! Ganhou uma cópia do anão {dwarf_opponent['name']}!")
        elif user_score < opponent_score:
            self.dwarves[user.id].append(dwarf_user.copy())  # Adversário vence
            await ctx.send(f"{user.mention} venceu a batalha! Ganhou uma cópia do anão {dwarf_user['name']}!")
        else:
            await ctx.send("A batalha terminou em empate! Ninguém ganha nada.")

    @commands.hybrid_command(with_app_command=True)
    async def batalha_selvagem(self, ctx:commands.Context, dwarf_index: int):
        """Batalha contra um anão selvagem."""
        if ctx.author.id not in self.dwarves or dwarf_index <= 0 or dwarf_index > len(self.dwarves[ctx.author.id]):
            await ctx.send(f"Anão inválido, {ctx.author.mention}. Verifique sua lista com `!meus_anoes`.")
            return

        dwarf_user = self.dwarves[ctx.author.id][dwarf_index - 1]
        wild_dwarf = self.generate_dwarf()  # Gera um anão selvagem aleatório

        user_score = dwarf_user["strength"] + dwarf_user["intelligence"] + dwarf_user["agility"]
        wild_score = wild_dwarf["strength"] + wild_dwarf["intelligence"] + wild_dwarf["agility"]

        if user_score > wild_score:
            self.dwarves[ctx.author.id].append(wild_dwarf.copy())  # Jogador vence
            await ctx.send(f"Você venceu a batalha contrao anão selvagem {wild_dwarf['name']} e ganhou uma cópia dele!")
        
        else: 
            self.balances[ctx.author.id] = max(0, int(self.balances[ctx.author.id] * 0.9)) 
            # Perde 10% do saldo 
            await ctx.send(f"Você perdeu para o anão selvagem {wild_dwarf['name']}! Perdeu 10% do saldo. Saldo atual: {self.balances[ctx.author.id]} moedas.")


    @commands.hybrid_command(with_app_command=True)
    async def vender_jogador(self, ctx:commands.Context, user: discord.User, dwarf_index: int, price: int):
        """Vende um anão para outro jogador."""
        if ctx.author.id not in self.dwarves or dwarf_index <= 0 or dwarf_index > len(self.dwarves[ctx.author.id]):
            await ctx.send(f"Anão inválido, {ctx.author.mention}. Verifique sua lista com `!meus_anoes`.")
            return

        if user.id not in self.balances or self.balances[user.id] < price:
            await ctx.send(f"O jogador {user.mention} não tem moedas suficientes para comprar o anão.")
            return

        dwarf = self.dwarves[ctx.author.id].pop(dwarf_index - 1)
        self.dwarves[user.id].append(dwarf)
        self.balances[ctx.author.id] += price
        self.balances[user.id] -= price

        await ctx.send(f"Você vendeu o anão {dwarf['name']} para {user.mention} por {price} moedas. Saldo atual: {self.balances[ctx.author.id]} moedas.")


async def setup(bot):
    await bot.add_cog(DwarfMarket(bot))