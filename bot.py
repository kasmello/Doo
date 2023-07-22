# bot.py
import os
import json
import discord
import random
from discord.ext import commands

from dotenv import load_dotenv
from lyrics_getter import return_lyrics

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
    

intents = discord.Intents.default()
intents.message_content = True

class DooBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.playing_emoji_game = False
        self.emoji_dict = None
        self.emoji_score = 0
        self.current_emoji = None

    def reset_emoji_game(self):
        self.playing_emoji_game = False
        self.emoji_score = 0
        self.current_emoji = None

    async def play_emoji_turn(self,ctx):
        self.current_emoji = random.choice(list(self.emoji_dict.keys()))
        await ctx.send(f"Current Emoji: {self.current_emoji}")

    async def check_emoji(self,ctx,emoji):
        if emoji in self.emoji_dict[self.current_emoji]:
            await ctx.send(f"**Good!**")
            self.emoji_score += 1
            await self.play_emoji_turn(ctx)
        else:
            await ctx.send(f"**Ruh Roh!**\nGame over!\n\n\nScore: {self.emoji_score}")
            self.reset_emoji_game()
        


bot = DooBot(command_prefix='!',intents=intents)

@bot.command()
async def mcmbuild(ctx,*args):
    await ctx.send(f'I build you a {args[0]} house, you peasant!')
    print(f'{ctx.message.author.name} has requested for a minecraft build')

@bot.command()
async def mcmhelp(ctx, *args):
    await ctx.message.author.send(f'**Hello** @{ctx.message.author.name}, here are some helpful commands :)\n\n\
                                  Type ***!mcmbuild*** *material_of_your_choice* to make a house of that material\n\
                                  Type ***!mcmsad*** to get a sad song delivered to your nearest chat\n\
                                  Type ***!mcmemojigame*** to play the emoji game ;)\n\nHave fun!')
    print(f'{ctx.message.author.name} has requested for help')


@bot.command()
async def mcmemojigame(ctx, *args):
    with open('emoji_pairing.json', 'r', encoding='utf-8') as file:

        bot.emoji_dict  = json.load(file)
        bot.playing_emoji_game = True
        await ctx.send("**Let's play the emoji game, where anyone can play!🍆🍆🍆**\nI type an emoji, you type one that matches it\nMake sure for each response, you put ***!choose*** beforehand.")
        await bot.play_emoji_turn(ctx)

@bot.command()
async def choose(ctx, *args):
    if bot.playing_emoji_game:
        if len(args) > 1 or len(args[0]) > 1:
            await ctx.send("You sent more than 1 emoji, I'm' only taking the first!")
        await bot.check_emoji(ctx,args[0][0])

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
