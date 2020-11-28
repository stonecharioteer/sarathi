"""Sarathi - A discord bot to steer through the battlefield of knowledge"""
import sys
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

import til

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = os.getenv("DISCORD_GUILD")

bot = commands.Bot(
    command_prefix="/",
    description="A small bot to help me manage my knowledge base on my blog.",
    case_insensitive=True,
    )


@bot.event
async def on_ready():
    """Behaviour when ready"""
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
    sys.stdout.write(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    members = '\n - '.join([member.name for member in guild.members])
    sys.stdout.write(f'Guild Members:\n - {members}\n')


@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )


@bot.command(
    name="til",
    help=(
        "A command to help manage the today-i-learned database of my blog. "
        "Use as `/til add <input>` or, `/til find <topic>` or `/til <input>`."
        ))
async def today_i_learned(ctx, *query):
    """Today I Learned"""
    response = til.process_query(*query)
    await ctx.send(response)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise Exception("Error encountered: {} x {} x {}".format(event, args, kwargs))


def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
