from discord.ext import commands
import os
prefixo = ',s'

class ProibidoEntrar(commands.Cog):
        
    def __init__(self, bot):
        self.bot = bot
        self.banned_file = 'Proibido/proibido.txt'  # Caminho para o arquivo de IDs proibidos
        self.ensure_file_exists()

    def ensure_file_exists(self):
        # Garante que o arquivo de IDs proibidos exista
        if not os.path.exists(self.banned_file):
            os.makedirs(os.path.dirname(self.banned_file), exist_ok=True)
            with open(self.banned_file, 'w', encoding='utf-8') as f:
                pass  # Cria o arquivo se não existir

    def read_banned_ids(self):
        # Lê os IDs do arquivo e os retorna como uma lista de inteiros
        with open(self.banned_file, 'r', encoding='utf-8') as f:
            ids = f.read().splitlines()
        return [int(id) for id in ids if id.isdigit()]

    def write_banned_ids(self, ids):
        # Escreve a lista de IDs no arquivo
        with open(self.banned_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(map(str, ids)))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        banned_ids = self.read_banned_ids()
        if member.id in banned_ids:
            #await member.kick(reason="ID proibido de entrar no servidor.")
            await member.ban(reason="ID proibido de entrar no servidor.")
            print(f"{member.id} {member.name} foi expulso por estar na lista de IDs proibidos.")

    # Comando híbrido para adicionar um ID à lista de IDs proibidos
    @commands.hybrid_command(with_app_command=True, help="Adiciona um ID à lista de IDs proibidos.")
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def proibir_entrada(self, ctx:commands.Context, id: int):
        banned_ids = self.read_banned_ids()
        if id not in banned_ids:
            banned_ids.append(id)
            self.write_banned_ids(banned_ids)
            await ctx.send(f"ID {id} adicionado à lista de IDs proibidos.")
        else:
            await ctx.send(f"O ID {id} já está na lista de IDs proibidos.")

    # Comando híbrido para remover um ID da lista de IDs proibidos
    @commands.hybrid_command(with_app_command=True, help="Remove um ID da lista de IDs proibidos.")
    @commands.has_permissions(administrator=True)  # Requer permissões de administrador
    async def permitir_entrada(self, ctx:commands.Context, id: int):
        banned_ids = self.read_banned_ids()
        if id in banned_ids:
            banned_ids.remove(id)
            self.write_banned_ids(banned_ids)
            await ctx.send(f"ID {id} removido da lista de IDs proibidos.")
        else:
            await ctx.send(f"O ID {id} não foi encontrado na lista de IDs proibidos.")

async def setup(bot):
    await bot.add_cog(ProibidoEntrar(bot))