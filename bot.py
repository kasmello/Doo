# bot.py
import os

import discord
from discord.ext import commands
from discord.ext.commands.bot import Bot

from dotenv import load_dotenv
from lyrics_getter import return_lyrics

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
    

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)

@bot.command()
async def mcmbuild(ctx,*args):
    await ctx.send(f'I build you a {args[0]} house, you peasant!')
    print(f'{ctx.message.author.name} has requested for a minecraft build')

@bot.command()
async def mcmhelp(ctx, *args):
    await ctx.message.author.send(f'**Hello** @{ctx.message.author.name}, here are some helpful commands :)\n\n\
                                  Type ***!mcmbuild*** *material_of_your_choice* to make a house of that material\n\
                                  Type ***!mcmsad*** to get a sad song delivered to your nearest chat\n\nHave fun!')
    print(f'{ctx.message.author.name} has requested for help')

@bot.command()
async def mcmsad(ctx, *args):
    await ctx.send('Hold your horses! A sad song is coming!')
    print(f'{ctx.message.author.name} has requested for Joji Lyrics')
    lyrics = return_lyrics()
    for item in lyrics:
        await ctx.send(f'```\n{item}\n```')

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

bot.run(TOKEN)

