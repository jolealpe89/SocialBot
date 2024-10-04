
import datetime
import asyncio
import traceback
from functools import partial
from random import shuffle
from discord import *
import discord
from discord.ext import commands
from yt_dlp import *
import yt_dlp as ytdl
import re
import datetime
from gtts import gTTS
import os

prefixo = ',s'

URL_REG = re.compile(r'https?://(?:www\.)?.+')
YOUTUBE_VIDEO_REG = re.compile(r"(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)")
YOUTU_BE=re.compile(r"(https?://)?(www\.)?youtu\.be\?v=([-\w]+)")
#filters = {
#    'nightcore': 'aresample=48000,asetrate=48000*1.25'
#}
filters = {
    'nightcore': 'aresample=48000,asetrate=48000*1.05',
    'radio_effect': 'aresample=8000,highpass=f=200,lowpass=f=3000,volume=0.8',
    'vinyl_effect': 'anequalizer=f=1000:width_type=h:width=200:g=-10,asetrate=44100*1.1,atempo=1.1,noise=alls=20:allf=t+u'
}


def utc_time():
    return datetime.datetime.now(datetime.timezone.utc)


YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'retries': 5,
    # 'default_search': 'auto',
    'extract_flat': True,
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-nostdin'
                      ' -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


def fix_characters(text: str):
    replaces = [
        ('&quot;', '"'),
        ('&amp;', '&'),
        ('(', '\u0028'),
        (')', '\u0029'),
        ('[', '【'),
        (']', '】'),
        ("  ", " "),
        ("*", '"'),
        ("_", ' '),
        ("{", "\u0028"),
        ("}", "\u0029"),
    ]
    for r in replaces:
        text = text.replace(r[0], r[1])

    return text


ytdl = YoutubeDL(YDL_OPTIONS)


def is_requester():
    def predicate(ctx):
        player = ctx.bot.players.get(ctx.guild.id)
        if not player:
            return True
        if ctx.author.guild_permissions.manage_channels:
            return True
        if ctx.author.voice and not any(
                m for m in ctx.author.voice.channel.members if not m.bot and m.guild_permissions.manage_channels):
            return True
        if player.current['requester'] == ctx.author:
            return True

    return commands.check(predicate)


class MusicPlayer:

    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.bot = ctx.bot
        self.queue = []
        self.current = None
        self.event = asyncio.Event()
        self.now_playing = None
        self.timeout_task = None
        self.channel: discord.VoiceChannel = None
        self.disconnect_timeout = 180
        self.loop = False
        self.exiting = False
        self.nightcore = False
        self.radio_effect = False  # Adicionando a opção de efeito de rádio antigo
        self.vinyl_effect = False
        self.fx = []
        self.no_message = False
        self.locked = False
        self.api_key = 'a49f9a21c98e39b951544884c2e64852'

    async def player_timeout(self):
        await asyncio.sleep(self.disconnect_timeout)
        self.exiting = True
        self.bot.loop.create_task(self.ctx.cog.destroy_player(self.ctx))

    async def process_next(self):

        self.event.clear()

        if self.locked:
            return

        if self.exiting:
            return

        try:
            self.timeout_task.cancel()
        except:
            pass

        if not self.queue:
            self.timeout_task = self.bot.loop.create_task(self.player_timeout())

            remaining = int((utc_time() + datetime.timedelta(seconds=self.disconnect_timeout)).timestamp())

            embed = discord.Embed(
                description=f"Como não tenho mais pedidos...\nIrei me retirar <t:{remaining}:R> caso não me peçam novas músicas.",
                color=discord.Colour.red())
            await self.ctx.send(embed=embed)
            return

        await self.start_play()

    async def renew_url(self):

        info = self.queue.pop(0)

        self.current = info

        try:
            url = info['webpage_url']
        except KeyError:
            url = info['url']
            
        if (yt_url := YOUTUBE_VIDEO_REG.match(url)):
            url = yt_url.group()
        
        if (yt_url := YOUTU_BE.match(url)):
            url = yt_url.group()

        to_run = partial(ytdl.extract_info, url=url, download=False)
        info = await self.bot.loop.run_in_executor(None, to_run)

        return info

    def ffmpeg_after(self, e):

        if e:
            print(f"ffmpeg error: {e}")

        self.event.set()

    async def start_play(self):

        await self.bot.wait_until_ready()

        if self.exiting:
            return

        self.event.clear()

        try:
            info = await self.renew_url()
        except Exception as e:
            traceback.print_exc()
            try:
                await self.ctx.send(embed=discord.Embed(
                    description=f"**Ocorreu um erro durante a reprodução da música:\n[{self.current['title']}]({self.current['webpage_url']})** ```css\n{e}\n```",
                    color=discord.Colour.red()))
            except:
                pass
            self.locked = True
            await asyncio.sleep(6)
            self.locked = False
            await self.process_next()
            return

        url = ""
        for format in info['formats']:
            if format['ext'] == 'm4a':
                url = format['url']
                break
        if not url:
            url = info['formats'][0]['url']

        ffmpg_opts = dict(FFMPEG_OPTIONS)

        self.fx = []

        if self.nightcore:
            self.fx.append(filters['nightcore'])
        
        if self.radio_effect:  # Adicionando o filtro de rádio antigo
            self.fx.append(filters['radio_effect'])

        
        if self.vinyl_effect:
            self.fx.append(filters['vinyl_effect'])

        if self.fx:
            ffmpg_opts['options'] += (f" -af \"" + ", ".join(self.fx) + "\"")

        try:
            if self.channel != self.ctx.me.voice.channel:
                self.channel = self.ctx.me.voice.channel
                await self.ctx.voice_client.move_to(self.channel)
        except AttributeError:
            print("teste: Bot desconectado após obter download da info.")
            return

        source = discord.FFmpegPCMAudio(url, **ffmpg_opts)
        
        self.ctx.voice_client.play(source, after=lambda e: self.ffmpeg_after(e))

        if self.no_message:
            self.no_message = False
        else:
            try:
                
                embed = discord.Embed(
                    description=f"**Tocando agora:**\n[**{info['title']}**]({info['webpage_url']})\n\n**Duração:** `{datetime.timedelta(seconds=info['duration'])}`\n**Social Bot foi chamado por: {self.ctx.message.author.mention}**",
                    color=self.ctx.me.colour,
                )

                thumb = info.get('thumbnail')

                if self.loop:
                    embed.description += " **| Repetição:** `ativada`"

                if self.nightcore:
                    embed.description += " **| Nightcore:** `Ativado`"
                    
                if self.radio_effect:
                    embed.description += " **| Efeito de Rádio:** `Ativado`"
                
                if self.vinyl_effect:
                    embed.description += " **| Efeito de Vinyl:** `Ativado`"

                if thumb:
                    embed.set_thumbnail(url=thumb)

                self.now_playing = await self.ctx.send(embed=embed)

            except Exception:
                traceback.print_exc()

        await self.event.wait()

        source.cleanup()

        if self.loop:
            self.queue.insert(0, self.current)
            self.no_message = True

        self.current = None

        await self.process_next()

class music(commands.Cog):
    def __init__(self, bot):

        if not hasattr(bot, 'players'):
            bot.players = {}

        self.bot = bot

    def get_player(self, ctx):
        try:
            player = ctx.bot.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.bot.players[ctx.guild.id] = player

        return player

    async def destroy_player(self, ctx):

        ctx.player.exiting = True
        ctx.player.loop = False

        try:
            ctx.player.timeout_task.cancel()
        except:
            pass

        del self.bot.players[ctx.guild.id]

        if ctx.me.voice:
            await ctx.voice_client.disconnect()
        elif ctx.voice_client:
            ctx.voice_client.cleanup()

    async def search_yt(self, item:str):
        if (yt_url := YOUTUBE_VIDEO_REG.match(str(item))):
            item = yt_url.group()
        elif not URL_REG.match(item):
            item = f"ytsearch:{item}"
    
        try:
            to_run = partial(ytdl.extract_info, url=item, download=False)
            info = await self.bot.loop.run_in_executor(None, to_run)
        except Exception as e:
            print(f"Erro ao buscar informações do vídeo: {e}")
            return []
    
        if info is None:
            return []
    
        entries = info.get("entries", [info])
    
        if info["extractor_key"] == "YoutubeSearch":
            entries = entries[:1]
    
        tracks = []
    
        for t in entries:
            url = t.get('webpage_url') or t.get('url') or ''
    
            if not URL_REG.match(url):
                url = f"https://www.youtube.com/watch?v={url}"
    
            title = t.get('title', '')
            duration = t.get('duration', 0)
            uploader = t.get('uploader', '')
    
            tracks.append(
                {
                    'url': url,
                    'title': fix_characters(title),
                    'uploader': uploader,
                    'duration': duration
                }
            )
    
        return tracks

    #função tocar
    #@commands.command(name="play", help=f"Toca uma música do YouTube. Exemplo: `{prefixo}play Cooler Than Me`", aliases=['p', 'tocar','nandomoura'])
    @commands.hybrid_command(name="play", help=f"Toca uma música do YouTube.")
    async def p(self, ctx:commands.Context, *, query: str):
        await ctx.send("Ok!")
    #async def p(self, ctx, *, query: str = "Rick Astley - Never Gonna Give You Up "):
        if ctx.author.bot:
            return False
        if not ctx.author.voice:
            # if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            embedvc = discord.Embed(
                colour=1646116,  # grey
                description='Eu vou tocar música pras paredes, seu macaco? Entra num canal de voz primeiro!'
            )
            await ctx.send(embed=embedvc)
            return
        

        #query = str(query.strip("<>"))
        # Adiciona aspas no início e no fim do parâmetro query
        #if "PL" not in query:
        #    query = f'"{query}"'

        
        try:
            
            songs = await self.search_yt(query)
        except Exception as e:
            traceback.print_exc()
            embedvc = discord.Embed(
                colour=12255232,  # red
                description=f'**Algo deu errado ao processar sua busca:**\n```css\n{repr(e)}```'
            )
            await ctx.send(embed=embedvc)
            return

        if not songs:
            embedvc = discord.Embed(
                colour=12255232,  # red
                description=f'Não houve resultados para sua busca: **{query}**'
            )
            await ctx.send(embed=embedvc)
            return

        if not ctx.player:
            ctx.player = self.get_player(ctx)

        player = ctx.player

        vc_channel = ctx.author.voice.channel

        if (size := len(songs)) > 1:
            txt = f"Você adicionou **{size} músicas** na fila!"
        else:
            txt = f"Pois não mestre {ctx.message.author.mention}, tocarei pra você **{songs[0]['title']}** com muito prazer!"
        for song in songs:
            song['requester'] = ctx.author
            player.queue.append(song)

        embedvc = discord.Embed(
            colour=32768,  # green
            description=f"{txt}\n\n[🎵](Utilize `{prefixo}help` para ver os comandos)"
        )
        await ctx.send(embed=embedvc)

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            player.channel = vc_channel
            await vc_channel.connect(timeout=None, reconnect=False)

        if not ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await player.process_next()

    async def  commandName(self, ctx:commands.Context):
        await ctx.send("template command")
    
    #@commands.command(name="pause", help="Pausa a música atual", aliases=['pausar'])
    @commands.hybrid_command(name="pause", help="Pausa a música atual.")
    async def pause (self, ctx):
        sp = ctx.voice_client.is_playing()
        p = ctx.voice_client.is_paused()
        if sp== True:
            if p == False:
                ctx.voice_client.pause() 
                await ctx.message.add_reaction('⏸️')               
            else:
                if p == True:
                    await ctx.send('Música pausada.', delete_after=10)
        else:
            if p == True:
                await ctx.send('A música já está pausada, seu mamaco!', delete_after=10)

            else:
                await ctx.send("Tô ocupado jogando Alcarnia.", delete_after=10)
    
    #@commands.command(name="resume", help="Volta a tocar música de onde parou", aliases=['resumir'])
    @commands.hybrid_command(name="resume", help="Volta a tocar música de onde parou.")
    async def resume (self, ctx):
        p = ctx.voice_client.is_playing()
        sp = ctx.voice_client.is_paused()
        if sp== True:
            if p == False:
                ctx.voice_client.resume() 
                await ctx.message.add_reaction('▶️')
            else:
                if p == True:
                    await ctx.send('Música resumida.', delete_after=10)
        else:
            if p == True:
                await ctx.send('A música já está tocando, seu mamaco!', delete_after=10)

            else:
                await ctx.send("Tô ocupado jogando Alcarnia.", delete_after=10)
        
    #@commands.command(name="queue", help="Mostra as atuais músicas da fila.", aliases=['q', 'fila'])
    @commands.hybrid_command(name="queue", help="Mostra as atuais músicas da fila.")
    async def q(self,ctx):

        player = ctx.player

        if not player:
            await ctx.reply("Não há player ativo no momento...")
            return

        if not player.queue:
            embedvc = discord.Embed(
                colour=1646116,
                description='Não existe músicas na fila no momento.'
            )
            await ctx.send(embed=embedvc)
            return
        retval = ""

        def limit(text):
            if len(text) > 30:
                return text[:28] + "..."
            return text

        for n, i in enumerate(player.queue[:20]):
            if i["duration"] is None:
                duration = datetime.timedelta(seconds=0)
            else:
                duration = datetime.timedelta(seconds=i["duration"])
            
            retval += f'**{n + 1} | `{duration}` - ** [{limit(i["title"])}]({i["url"]}) | {i["requester"].mention}\n'
            
        
            #retval += f'**{n + 1} | `{datetime.timedelta(seconds=i["duration"])}` - ** [{limit(i["title"])}]({i["url"]}) | {i["requester"].mention}\n'

        if (qsize := len(player.queue)) > 20:
            retval += f"\nE mais **{qsize - 20}** música(s)"

        embedvc = discord.Embed(
            colour=12255232,
            description=f"{retval}"
        )
        await ctx.send(embed=embedvc)

    #@is_requester()
    #@commands.command(name="skip", help="Pula a música atual que está tocando.", aliases=['pauloguedes', 's'])
    @commands.hybrid_command(name="skip", help="Pula a música atual que está tocando.")
    async def skip(self, ctx:commands.Context):
        await ctx.send("Ok!")

        player = ctx.player

        if not player:
            await ctx.reply("Não há players ativo no momento...")
            return

        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.reply("Não estou tocando algo...")
            return

        await ctx.message.add_reaction('🦘')
        player.loop = False
        ctx.voice_client.stop()

    #@skip.error  # Erros para kick
    #async def skip_error(self, ctx, error):
    #    if isinstance(error, commands.CheckFailure):
    #        embedvc = discord.Embed(
    #            colour=12255232,
    #            description=f"Você deve ser dono da música adicionada ou ter a permissão de **Gerenciar canais** para pular músicas."
    #        )
    #        await ctx.send(embed=embedvc)
    #    else:
    #        raise error
#
    #@commands.command(name="shuffle", aliases=["misturar"], help="Misturar as músicas da fila")
    @commands.hybrid_command(name="shuffle", help="Misturar as músicas da fila")
    async def shuffle_(self, ctx):

        player = ctx.player

        embed = discord.Embed(color=discord.Colour.red())

        if not player:
            embed.description = "Estou tocando alguma coisa? Acho que não, né?"
            await ctx.send(embed=embed)

        if len(player.queue) < 3:
            embed.description = "A fila tem que ter no mínimo 3 músicas para ser misturada."
            await ctx.send(embed=embed)
            return

        shuffle(player.queue)

        embed.description = f"**Você misturou as músicas da fila.**"
        embed.colour = discord.Colour.green()
        await ctx.send(embed=embed)
    #função tocar com loop
    #@commands.command(name="playloop", help=f"Toco a música já com loop ativado. Exemplo: `{prefixo}poop Mike Postner Cooler than me`", aliases=['poop','marcospontes'])
    @commands.hybrid_command()
    async def poop(self, ctx, *, query: str = "Rick Astley - Never Gonna Give You Up "):
        if not ctx.author.voice:
            # if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            embedvc = discord.Embed(
                colour=1646116,  # grey
                description='Eu vou tocar música pras paredes, seu macaco? Entra num canal de voz primeiro!'
            )
            await ctx.send(embed=embedvc)
            return

        query = query.strip("<>")

        try:
            songs = await self.search_yt(query)
        except Exception as e:
            traceback.print_exc()
            embedvc = discord.Embed(
                colour=12255232,  # red
                description=f'**Algo deu errado ao processar sua busca:**\n```css\n{repr(e)}```'
            )
            await ctx.send(embed=embedvc)
            return

        if not songs:
            embedvc = discord.Embed(
                colour=12255232,  # red
                description=f'Não houve resultados para sua busca: **{query}**'
            )
            await ctx.send(embed=embedvc)
            return

        if not ctx.player:
            ctx.player = self.get_player(ctx)

        player = ctx.player

        vc_channel = ctx.author.voice.channel

        if (size := len(songs)) > 1:
            txt = f"Você adicionou **{size} músicas** na fila!"
        else:
            txt = f"Pois não mestre {ctx.message.author.mention}, tocarei pra você **{songs[0]['title']}** com muito prazer e ainda repetirei!"
        for song in songs:
            song['requester'] = ctx.author
            player.queue.append(song)
            #tentativa de loop
            player.loop = not player.loop

        embedvc = discord.Embed(
            colour=32768,  # green
            description=f"{txt}\n\n[🎵](Utilize `{prefixo}help` para ver os comandos)"
        )
        await ctx.send(embed=embedvc)

        if not ctx.voice_client or not ctx.voice_client.is_connected():
            player.channel = vc_channel
            await vc_channel.connect(timeout=None, reconnect=False)

        if not ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            await player.process_next()
    @commands.hybrid_command(name = "repeat", help="Ativar/Desativar a repetição da música atual")
    #@commands.command(name = "repeat", help="Ativar/Desativar a repetição da música atual", aliases=['loop', 'repetir'])
    async def repeat(self, ctx):

        player = ctx.player

        embed = discord.Embed(color=discord.Colour.red())

        if not player:
            embed.description = "Não estou tocando algo no momento"
            await ctx.send(embed=embed)

        player.loop = not player.loop

        embed.colour = discord.Colour.green()
        embed.description = f"**Repetição {'ativada para a música atual' if player.loop else 'desativada'}.**"

        await ctx.send(embed=embed)
    #@commands.command(name = "nightcore", aliases=["nc"], help="Ativar/Desativar o efeito nightcore (Música acelerada com tom mais agudo.)")
    @commands.hybrid_command(name = "nightcore", help="Ativar/Desativar o efeito nightcore (Música acelerada com tom mais agudo.)")
    async def nightcore(self, ctx):

        player = ctx.player

        embed = discord.Embed(color=discord.Colour.red())

        if not player:
            embed.description = "Não estou tocando algo no momento"
            await ctx.send(embed=embed)

        player.nightcore = not player.nightcore
        player.queue.insert(0, player.current)
        player.no_message = True

        ctx.voice_client.stop()

        embed.description = f"**Efeito nightcore {'ativado' if player.nightcore else 'desativado'}.**"
        embed.colour = discord.Colour.green()

        await ctx.send(embed=embed)

    @commands.hybrid_command(help="Ativar/Desativar o efeito radio.")
    async def radio(self, ctx):

        player = ctx.player

        embed = discord.Embed(color=discord.Colour.red())

        if not player:
            embed.description = "Não estou tocando algo no momento"
            await ctx.send(embed=embed)

        player.radio_effect = not player.radio_effect
        player.queue.insert(0, player.current)
        player.no_message = True

        ctx.voice_client.stop()

        embed.description = f"**Efeito radio {'ativado' if player.radio_effect else 'desativado'}.**"
        embed.colour = discord.Colour.green()

        await ctx.send(embed=embed)

    @commands.hybrid_command(help="Ativar/Desativar o efeito de vitrola.")
    async def vinyl(self, ctx):

        player = ctx.player

        embed = discord.Embed(color=discord.Colour.red())

        if not player:
            embed.description = "Não estou tocando algo no momento"
            await ctx.send(embed=embed)

        player.vinyl_effect = not player.vinyl_effect
        player.queue.insert(0, player.current)
        player.no_message = True

        ctx.voice_client.stop()

        embed.description = f"**Efeito vitrola {'ativado' if player.vinyl_effect else 'desativado'}.**"
        embed.colour = discord.Colour.green()

        await ctx.send(embed=embed)
    
    #@commands.command(name="cleare", help="Limpa a fila de músicas", aliases=['c'])
    @commands.hybrid_command(name="clearquery", help="Limpa a fila de músicas")
    async def cleare(self, ctx):
        player = ctx.player
    
        if not player:
            await ctx.reply("Não há players ativos no momento...")
            return
    
        if not player.queue:
            await ctx.reply("Não há nada na fila para ser removido.")
            return
    
        player.queue.clear()
        await ctx.message.add_reaction('👌')

    #@commands.command(name="stop",aliases=['parar', 'sair', 'leave', 'l', 'vaiprocaralho'], help="Parar o player e me desconectar do canal de voz.")
    @commands.hybrid_command(name="stop", help="Parar o player e me desconectar do canal de voz.")
    async def stop(self, ctx):

        embedvc = discord.Embed(colour=12255232)

        player = ctx.player

        if not player:
            embedvc.description = "Não há player ativo no momento..."
            await ctx.reply(embed=embedvc)
            return

        if not ctx.me.voice:
            embedvc.description = "Não estou conectado em um canal de voz."
            await ctx.reply(embed=embedvc)
            return

        if not ctx.author.voice or ctx.author.voice.channel != ctx.me.voice.channel:
            embedvc.description = "Você precisa estar no meu canal de voz atual para usar esse comando."
            await ctx.reply(embed=embedvc)
            return

        await self.destroy_player(ctx)

        embedvc.colour = 1646116
        embedvc.description =f'Obrigado e foi um prazer servi-lo, grande **{ctx.message.author.mention}**, sempre estarei à vossa disposição!'
        await ctx.reply(embed=embedvc)
    @commands.Cog.listener("on_voice_state_update")
    async def player_vc_disconnect(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):

        if member.id != self.bot.user.id:
            return

        if after.channel:
            return

        player: MusicPlayer = self.bot.players.get(member.guild.id)

        if not player:
            return

        if player.exiting:
            return

        embed = discord.Embed(description="**Desligando player por desconexão do canal.**", color=member.color)

        await player.ctx.channel.send(embed=embed)

        await self.destroy_player(player.ctx)


    async def cog_before_invoke(self, ctx):

        ctx.player = self.bot.players.get(ctx.guild.id)

        return True

    @commands.hybrid_command(with_app_command=True, help="Digite uma mensagem para o Bot repetir.")
    async def say(self, ctx: commands.Context, *, text: str):
        """Fala o texto no canal de voz"""
        # Verifica se o usuário está em um canal de voz
        if ctx.author.voice is None:
            await ctx.send("Você precisa estar em um canal de voz para usar esse comando.")
            return
        
        voice_channel = ctx.author.voice.channel

        # Verifica se o bot já está conectado a um canal de voz
        if ctx.voice_client is not None:
            if ctx.voice_client.channel != voice_channel:
                await ctx.voice_client.move_to(voice_channel)
        else:
            vc = await voice_channel.connect()

        try:
            # Converte texto para fala
            tts = gTTS(text=text, lang='pt-br')
            tts.save('temp.mp3')

            # Reproduz o áudio
            vc.play(discord.FFmpegPCMAudio('temp.mp3'))
            while vc.is_playing():
                await asyncio.sleep(2)

            # Desconecta do canal de voz
            await vc.disconnect()

            # Remove o arquivo temporário
            os.remove('temp.mp3')
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}")
            if vc.is_connected():
                await vc.disconnect()
            if os.path.exists('temp.mp3'):
                os.remove('temp.mp3')

    @commands.hybrid_command(with_app_command=True, help="Digite uma mensagem para o Bot repetir em japonês.")
    async def sayjp(self, ctx: commands.Context, *, text: str):
        """Fala o texto no canal de voz"""
        # Verifica se o usuário está em um canal de voz
        if ctx.author.voice is None:
            await ctx.send("Você precisa estar em um canal de voz para usar esse comando.")
            return
        
        voice_channel = ctx.author.voice.channel

        # Verifica se o bot já está conectado a um canal de voz
        if ctx.voice_client is not None:
            if ctx.voice_client.channel != voice_channel:
                await ctx.voice_client.move_to(voice_channel)
        else:
            vc = await voice_channel.connect()

        try:
            # Converte texto para fala
            tts = gTTS(text=text, lang='ja')
            tts.save('temp.mp3')

            # Reproduz o áudio
            vc.play(discord.FFmpegPCMAudio('temp.mp3'))
            while vc.is_playing():
                await asyncio.sleep(2)

            # Desconecta do canal de voz
            await vc.disconnect()

            # Remove o arquivo temporário
            os.remove('temp.mp3')
        except Exception as e:
            await ctx.send(f"Ocorreu um erro: {e}")
            if vc.is_connected():
                await vc.disconnect()
            if os.path.exists('temp.mp3'):
                os.remove('temp.mp3')
                

async def setup(client):
    await client.add_cog(music(client))