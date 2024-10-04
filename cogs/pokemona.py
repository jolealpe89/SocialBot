import discord
import random
import requests
from discord.ext import commands
from translate import Translator

class PokemonCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.hybrid_command(with_app_command=True, help='Sorteia um Pokémon pra você')
    #@commands.command(name='pokemon', help='Sorteia um Pokémon pra você', aliases=['pokeme'])
    async def pokemon(self, ctx:commands.Context):
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025")
        pokemon_list = response.json()['results']
        random_pokemon = random.choice(pokemon_list)
        pokemon_response = requests.get(random_pokemon['url'])
        pokemon_data = pokemon_response.json()
#
        # Deixa a primeira letra do nome do Pokémon em maiúsculo
        name = pokemon_data['name'].capitalize()
#
        # Deixa a primeira letra de cada palavra nos tipos em maiúsculo
        types = ', '.join([type['type']['name'].title() for type in pokemon_data['types']])
        
        description_response = requests.get(pokemon_data['species']['url'])
        description_data = description_response.json()
        description = next((entry['flavor_text'] for entry in description_data['flavor_text_entries'] if entry['language']['name'] == 'en'), 'No description available')
#
        # Traduzindo o texto para o português
        translator = Translator(to_lang="pt")
        translated_description = translator.translate(description)
        
#
        sprite_url = pokemon_data['sprites']['front_default']
        embed = discord.Embed(title=f"Você é um {name}!", description=translated_description, color=discord.Color(random.randint(0, 0xFFFFFF)))
        embed.set_image(url=sprite_url)
        embed.add_field(name="Tipo", value=types, inline=False)
        #await ctx.reply(embed=embed)
        await ctx.send(embed=embed)
    
    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

async def setup(bot):
    await bot.add_cog(PokemonCog(bot))