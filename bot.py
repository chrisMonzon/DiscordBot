## bot.py
import os
import discord
import youtube_dl
import random

from discord.voice_client import VoiceClient
from discord.ext import commands, tasks
from dotenv import load_dotenv

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        
#
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
#
client = discord.Client()
#
#@client.event
#async def on_ready():
#	for guild in client.guilds:
#		if guild.name == GUILD:
#			break
#	print(
#		f'{client.user} has connected to the following guild:\n'
#		f'{guild.name}(id: {guild.id})'
#	)
#
#@client.event
#async def on_message(message):
#	if message.author == client.user:
#		return
#	if 'bruh' in message.content.lower():
#		await message.channel.send('bruh')
#	elif message.content == 'raise-exception':
#		raise discord.DiscordException
#
#@client.event
#async def on_error(event, *args, **kwargs):
#    with open('err.log', 'a') as f:
#        if event == 'on_message':
#            f.write(f'Unhandled message: {args[0]}\n')
#        else:
#            raise
#
#client.run(TOKEN)

# bot.py


bot = commands.Bot(command_prefix='%')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command()
async def bruh(ctx, arg):
    await ctx.send('bruh man poo')

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)
    
@bot.command(name='bot_prefix')
async def prefix(ctx):
    await ctx.send('Prefix is set to %')

@bot.command(name='join')
async def join(ctx):
    channel = ctx.author.voice.channel
    try:
        await channel.connect()
    except discord.ClientException:
        await ctx.send('Already in a voice channel...')
    except discord.InvalidArgument:
        await ctx.send('This is not a voice channel...')
    else:
        await ctx.send('Ready to play audio in ' + channel.name)
    
@bot.command(name='leave')
async def leave(ctx):
    if ctx.member.voice is not None: #if author in voice channel
        server = ctx.message.guild.voice_client
        await server.disconnect()
    else:
        await ctx.send('Not connected to a voice channel.')
        
@bot.command(name='thud')
async def thud(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    
    # async with ctx.typing():
    url = 'https://youtu.be/829pvBHyG6I'
    player = await YTDLSource.from_url(url, loop=client.loop)
    voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
    
bot.run(TOKEN)
