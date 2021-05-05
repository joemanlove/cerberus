# discord_bot module for use with cerberus
# written by Joe Manlove
# forked from python music bot created Spring 2020
# modified extensively 4/25-27 2021

"""
discord_bot provides the discord integration for cerberus.

User settings should be included in the discord_config file.

Only the function discord_bot_go is intended for import.

Expected use:
-------------
from discord_bot import discord_bot_go
"""

# import settings from file
from config import discord_config
token = discord_config["token"]
prefix = discord_config["prefix"]

# import discord utilities
import discord
from discord.ext import commands, tasks

# initialize discord client
bot = discord.Client()

# set command prefix
bot = commands.Bot(command_prefix=prefix)
# the info command will prompt the bot to output the channel_id
bot.default_channel_id = discord_config["default_channel_id"]

class Message_for_Reddit:
    """
    Message_for_Reddit, a wrapper for reddit messages.

    Attributes
    ----------
    title : str
        the title of the message
    text : str
        the body of the message
    """
    def __init__(self, title, text=" "):
        """
        Initializes a message to be sent to the reddit bot.

        Parameters
        ----------
        title : str
            the title of the message
        text : str, optional
            the body of the message (default is " ")
        """
        self.title = title
        self.text = text

@tasks.loop(seconds=5)
async def check_for_posts():
    """
    Checks for new posts sent from the reddit bot. Runs every 5 seconds.
    """
    # call poll to check if there's a msg to receive
    if bot.reddit_connection.poll():
        # The recv method blocks when called, halting the bot until a msg is received
        msg = bot.reddit_connection.recv()
        print("Discord Bot got:")
        print(msg.title)
        print(msg.text)
        # the message will not trigger a command because it doesn't start with the command prefix
        await bot.default_channel.send(f"Cross-post from Reddit:\n{msg.title}:\n{msg.text}")

# On ready message
@bot.event
async def on_ready():
    await bot.wait_until_ready()
    # set the channel to send reddit messages to
    bot.default_channel = bot.get_channel(bot.default_channel_id)
    # start tasks
    check_for_posts.start()
    print(f'{bot.user.name} has connected to Discord!')

# ping command for testing purposes
@bot.command(name='ping')
async def ping(ctx):
    """
    Ping, to test if the bot is online.

    Parameters
    ----------
    ctx : Context
        the context for the command, automatically generated
    """
    await ctx.send(f'Pong{prefix}')

@bot.command(name='info')
async def info(ctx):
    """
    Info, collect the guild id and channel id.

    Parameters
    ----------
    ctx : Context
        the context for the command, automatically generated
    """
    await ctx.send(f'Info:\n\tChannel: {ctx.channel.id}\n\tGuild: {ctx.guild.id}')

@bot.command(name='set_channel')
async def set_channel(ctx):
    """
    Sets the channel for the bot to send reddit messages to. Doesn't persist if bot restarts.

    Parameters
    ----------
    ctx : Context
        the context for the command, automatically generated
    """
    bot.default_channel = ctx.channel
    await ctx.send('Channel set.')

@bot.command(name='reddit')
async def reddit(ctx, title, body):
    """
    Sends a message to reddit.

    Parameters
    ----------
    ctx : Context
        the context for the command, automatically generated
    title : str
        the title of the message to be sent
    body : str
        the body of the message to be sent
    """
    # wrap message for sending
    msg = Message_for_Reddit(title, body)
    # send message to the reddit_bot process
    bot.reddit_connection.send(msg)
    # confirm sending in discord
    await ctx.send('Sent to reddit.')

def discord_bot_go(reddit_connection):
    """
    Make the discord bot go brrrr....

    Parameters
    ----------
    reddit_connection
        half of a Pipe (multiprocessing) connecting the reddit process and the discord process
    """
    # extend the bot by making the connection one of its attributes
    # this means the commands will have access to it without it being global.
    bot.reddit_connection = reddit_connection
    # connect the bot to discord, includes robust error handling
    bot.run(token)
