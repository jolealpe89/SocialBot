import discord
import random
import asyncio
from discord.ext import commands
prefixo=",b"

class PokemonBattle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(with_app_command=True,help=f"Desafia um membro para uma batalha Pokémon.")
    async def desafiar(self, ctx:commands.Context, member: discord.Member):
        await ctx.send(f"{member.mention}, você foi desafiado para uma batalha Pokémon! Aceita o desafio? (sim/não)")

        def check(m):
            return m.author == member and m.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"{member.mention} não respondeu a tempo. Desafio cancelado.")
            return

        if response.content.lower() != 'sim':
            await ctx.send(f"{member.mention} recusou o desafio. Batalha cancelada.")
            return

        await ctx.send(f"{member.mention} aceitou o desafio! Vamos começar a batalha Pokémon.")

        # Criar Pokémon para ambos os membros
        pokemon1 = await self.create_pokemon(ctx, ctx.author)
        pokemon2 = await self.create_pokemon(ctx, member)

        await ctx.send(f"{ctx.author.mention}, vai {pokemon1['nome']}!")
        await ctx.send(f"{member.mention}, vai {pokemon2['nome']}!")

        while pokemon1['vida'] > 0 and pokemon2['vida'] > 0:
            await self.attack(ctx, ctx.author, member, pokemon1, pokemon2)
            if pokemon2['vida'] <= 0:
                #await ctx.send(f"{member.mention} ganhou a batalha!")
                await ctx.send(f"{ctx.author.mention} ganhou a batalha!")
                break

            await self.attack(ctx, member, ctx.author, pokemon2, pokemon1)
            if pokemon1['vida'] <= 0:
                #await ctx.send(f"{ctx.author.mention} ganhou a batalha!")
                await ctx.send(f"{member.mention} ganhou a batalha!")
                break

    async def attack(self, ctx, attacker, defender, attacker_pokemon, defender_pokemon):
        await ctx.send(f"{attacker.mention}, escolha um ataque para {attacker_pokemon['nome']}:")
        try:
            attack_name = await self.choose_attack_name(ctx, attacker)
        except asyncio.TimeoutError:
            await ctx.send(f"{attacker.mention} não escolheu um ataque a tempo. Batalha cancelada.")
            return

        attack_type = random.choice(["Água", "Fogo", "Grama", "Elétrico"])  # Exemplo de tipos
        attack_power = random.randint(10, 30)
        attack_accuracy = random.uniform(0.5, 1.0)

        # Simula o ataque e seus efeitos
        damage = int(attack_power * (attacker_pokemon['ataque'] / defender_pokemon['defesa']) * attack_accuracy)
        defender_pokemon['vida'] -= damage

        await ctx.send(f"{attacker_pokemon['nome']} usou {attack_name} ({attack_type})!")
        await ctx.send(f"{defender_pokemon['nome']} perdeu {damage} pontos de vida. Vida restante: {defender_pokemon['vida']}")

    async def choose_attack_name(self, ctx, member):
        await ctx.send(f"{member.mention}, escolha o nome do seu ataque:")
        def check(m):
            return m.author == member and m.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', timeout=30, check=check)
            return response.content
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError

    async def create_pokemon(self, ctx, member):
        await ctx.send(f"{member.mention}, escolha o nome do seu Pokémon:")
        def check(m):
            return m.author == member and m.channel == ctx.channel

        try:
            response = await self.bot.wait_for('message', timeout=30, check=check)
        except asyncio.TimeoutError:
            response = None

        if response and response.content:
            pokemon_name = response.content
        else:
            pokemon_name = f"Pokémon{random.randint(1, 100)}"

        # Aqui você pode implementar a criação de um Pokémon com atributos aleatórios
        pokemon = {
            'nome': pokemon_name,
            'vida': random.randint(50, 100),
            'ataque': random.randint(20, 40),
            'defesa': random.randint(10, 30),
            'velocidade': random.randint(5, 15)
        }
        return pokemon

async def setup(bot):
    await bot.add_cog(PokemonBattle(bot))
