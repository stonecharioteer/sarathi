"""Sarathi - A discord bot to steer through the battlefield of knowledge"""
import os
import sys
import discord
from discord.ext import commands
from discord.ext.commands import is_owner
from dotenv import load_dotenv

from sarathi import til
from sarathi.parser import ArgParseError, sarathi_parser

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
    help=til.help_text)
@is_owner()
async def today_i_learned(ctx, *query):
    """Today I Learned"""
    await ctx.send("Processing...")
    command = ["til"]+list(query)
    try:
        arguments = sarathi_parser.parse_args(command)
    except ArgParseError:
        await ctx.send(
            "Invalid Input. "
            "Use `/help til` to learn how to use this bot.")
    except Exception as e:
        raise Exception("`{}` failed unexpectedly.".format(e)) from e
    else:
        response = til.process_query(arguments, message=ctx.message)
        if isinstance(response, str):
            await ctx.send(response)
        elif isinstance(response, list):
            for item in response:
                if isinstance(item, discord.Embed):
                    await ctx.send(embed=item)
                else:
                    await ctx.send(item)


@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise Exception(
                "Error encountered: {} x {} x {}".format(event, args, kwargs))


def main():
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
