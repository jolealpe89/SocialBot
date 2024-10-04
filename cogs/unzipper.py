from discord.ext import commands
import zipfile
import os

class ZipExtractor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="unzip", with_app_command=True)
    async def unzip_file(self, ctx:commands.Context, file_name: str):
        """Descompacta um arquivo .zip na pasta raiz."""
        zip_file = f"{file_name}.zip"
        
        if not os.path.isfile(zip_file):
            await ctx.send(f"O arquivo `{zip_file}` não foi encontrado.")
            return
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Extrai os arquivos diretamente na pasta raiz
                zip_ref.extractall(os.getcwd())
            await ctx.send(f"O arquivo `{zip_file}` foi descompactado com sucesso.", ephemeral=True)
        except zipfile.BadZipFile:
            await ctx.send(f"O arquivo `{zip_file}` está corrompido ou não é um arquivo zip válido.", ephemeral=True)

# Setup da cog
async def setup(bot):
    await bot.add_cog(ZipExtractor(bot))
