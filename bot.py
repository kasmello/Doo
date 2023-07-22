# bot.py
import os
import json
import discord
import random
import asyncio
from discord.ext import commands


from dotenv import load_dotenv
from lyrics_getter import return_lyrics
from api_db import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
    

intents = discord.Intents.default()
intents.message_content = True


class DooBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix, intents=intents)
        self.channel_game_status = {}
        self.emoji_dict = None
        '''example of start:
        self.playing_emoji_game = False
        self.current_emoji = None
        self.emoji_time_left = 0
        self.who_answered = {},
        'player_scores': {}
        '''
        
        with open('phrases.json', 'r', encoding='utf-8') as file:

            self.phrases  = json.load(file)

    async def reset_emoji_game(self,ctx):
        self.channel_game_status[ctx.channel.id] = {
            'playing_emoji_game': False,
            'current_emoji': None,
            'emoji_time_left': 0,
            'who_answered': {},
            'player_scores': {}
        }
        await self.return_high_scores(ctx)

    async def return_high_scores(self,ctx):
        headers = "| Players | Servers | Scores |\n"
        place_id = ctx.guild.id if ctx.guild else ctx.channel.id
        place = ctx.guild.name if ctx.guild else "Private"
        top_5_place = grab_top_5_place(place_id)
        line = "| " + "|".join(["-" * (len(key) + 2) for key in ['Players','Servers','Scores']]) + " |\n"
        top_5_place_table = headers + line
        for row in top_5_place:
            try:
                user = await self.fetch_user(row['user_id'])
                user = user.name
            except discord.errors.NotFound:
                user = "Private"
            top_5_place_table += f"| {user} | {place} | {row['score']} |"

        # top_5_place_table += "```"
        await ctx.send(f"**Here are the top 5 scores for this server**\n\n{top_5_place_table}")
        top_5_global = grab_top_5_global()
        top_5_global_table = headers + line
        for row in top_5_global:
            try:
                user = await self.fetch_user(row['user_id'])
                user = user.name
            except discord.errors.NotFound:
                user = "Private"
            try:
                place = await self.fetch_guild(row['place_id'])
            except discord.errors.NotFound:
                place = "Private"
            top_5_global_table += f"| {user} | {place} | {row['score']} |\n"

        # top_5_global_table += "```"
        await ctx.send(f"**Here are the top 5 scores globally**\n{top_5_global_table}")


    async def get_all_emoji_scores_str(self,ctx):
        result = ''
        for k,v in self.channel_game_status[ctx.channel.id]['player_scores'].items():
            user = await self.fetch_user(k)
            user = user.mention
            result += f'{user} - {v}\n'
            place_id = ctx.guild.id if ctx.guild else ctx.channel.id
            is_new_high_score = insert_score(k,place_id,v)
            if is_new_high_score:
                await ctx.send(f"\n**{random.choice(self.phrases['nice'])}** {user} has just achieved a high score!🎊\n")
        return result


    async def play_emoji_turn(self,ctx):
        self.channel_game_status[ctx.channel.id]['current_emoji'] = random.choice(list(self.emoji_dict.keys()))
        await ctx.send(f"Current Emoji:")
        await ctx.send(self.channel_game_status[ctx.channel.id]['current_emoji'])
        
    async def check_emoji(self,ctx,emoji):
        print(f'{ctx.author.name} said {emoji}')

        if ctx.author.id in self.channel_game_status[ctx.channel.id]['who_answered'].keys():
            await ctx.send(f'You already answered {ctx.author.mention}!')

        elif emoji in self.emoji_dict[self.channel_game_status[ctx.channel.id]['current_emoji']]:
            await ctx.send(f"**{ctx.author.mention}, {random.choice(self.phrases['nice'])}!**")
            await ctx.send(f"You answered with {self.channel_game_status[ctx.channel.id]['emoji_time_left']} seconds left")
            self.channel_game_status[ctx.channel.id]['player_scores'][ctx.author.id] = self.channel_game_status[ctx.channel.id]['player_scores'].get(ctx.author.id,0)+1
            if self.channel_game_status[ctx.channel.id]['emoji_time_left'] <= 5:
                await ctx.send(random.choice(self.phrases['hurry up']))

            self.channel_game_status[ctx.channel.id]['emoji_time_left'] = 60
            self.channel_game_status[ctx.channel.id]['who_answered'] = {}
            await self.play_emoji_turn(ctx)

        else:
            if not ctx.guild:
                all_scores = await self.get_all_emoji_scores_str(ctx)
                await ctx.send(f"**{random.choice(self.phrases['oh no'])}**\nGame over!\
                               \n\nTotal Score: **{sum(self.channel_game_status[ctx.channel.id]['player_scores'].values())}**\
                               \n{all_scores}")  
                await self.reset_emoji_game(ctx)
            else:
                await ctx.send(f"**{random.choice(self.phrases['oh no'])}**\nThat's not right!")
                self.channel_game_status[ctx.channel.id]['who_answered'][ctx.author.id]=emoji
        
    async def countdown(self, ctx):
        while self.channel_game_status[ctx.channel.id]['emoji_time_left'] > 0:
            await asyncio.sleep(1)
            self.channel_game_status[ctx.channel.id]['emoji_time_left'] -= 1

        if self.channel_game_status[ctx.channel.id]['playing_emoji_game']: #this is to prevent the game over message from presenting twice
            all_scores = await self.get_all_emoji_scores_str(ctx)
            await ctx.send(f"**{random.choice(self.phrases['time up'])}**\nGame over!\
                               \nTotal Score: **{sum(self.channel_game_status[ctx.channel.id]['player_scores'].values())}**\
                               \n{all_scores}")  
            await self.reset_emoji_game(ctx)
            



bot = DooBot(command_prefix='!',intents=intents)

@bot.command()
async def mcmbuild(ctx,*args):
    await ctx.send(f'I build you a {args[0]} house, you peasant!')
    print(f'{ctx.author.name} has requested for a minecraft build')

@bot.command()
async def mcmhelp(ctx, *args):
    await ctx.author.send(f'**Hello** {ctx.author.mention}, here are some helpful commands :)\n\n\
                                  Type ***!mcmbuild*** *material_of_your_choice* to make a house of that material\n\
                                  Type ***!mcmsad*** to get a sad song delivered to your nearest chat\n\
                                  Type ***!mcmemojigame*** to play the emoji game ;)\n\nHave fun!')
    print(f'{ctx.author.name} has requested for help')


@bot.command()
async def mcmemojigame(ctx, *args):
    try:
        if bot.channel_game_status[ctx.channel.id]['playing_emoji_game']:
            await ctx.send("This channel is already playing!")
            return
    except KeyError:
        print(f'No previous game state found for {ctx.channel.id}, making one now')

    if not bot.emoji_dict:
        with open('emoji_pairing.json', 'r', encoding='utf-8') as file:
            bot.emoji_dict  = json.load(file)

    bot.channel_game_status[ctx.channel.id] = { #each unique channel can play
        'playing_emoji_game': True,
        'current_emoji': None,
        'emoji_time_left': 60,
        'who_answered': {},
        'player_scores': {}
    }
    await ctx.send("**Let's play the emoji game, where anyone can play!🍆🍆🍆**\n\nI type an emoji, you type one that suits it.\
                    \nYou have 60 seconds to decide on an answer before the game is over.\nMake sure for each response, you put ***!choose*** beforehand.\n")
    await bot.play_emoji_turn(ctx)
    await bot.countdown(ctx)

@bot.command()
async def choose(ctx, *args):
    if bot.channel_game_status[ctx.channel.id]['playing_emoji_game']:
        if len(args) > 1 or len(args[0]) > 1:
            await ctx.send("You sent more than 1 emoji, I'm only taking the first!")
        await bot.check_emoji(ctx,args[0][0])

@bot.command()
async def mcmsad(ctx, *args):
    await ctx.send(f'{random.choice(bot.phrases["wait"])} A sad song is coming!')
    print(f'{ctx.author.name} has requested for Joji Lyrics')
    lyrics = return_lyrics()
    for item in lyrics:
        await ctx.send(f'```\n{item}\n```')

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

bot.run(TOKEN)

