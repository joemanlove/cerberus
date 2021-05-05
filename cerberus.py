# Cerberus - the multiheaded bot
# written by Joe Manlove
# created 4/25-27 2021

"""
Cerberus

Uses multiprocessing to implment a single bot connected to both reddit and discord.
That's actually a bit of a lie, it's more like a single beast with a reddit head and a discord head.
"""

# import the functions that run the individual bots
from discord_bot import discord_bot_go
from reddit_bot import reddit_bot_go

# multiprocessing lets it work together
import multiprocessing as mp


if __name__ == '__main__':
    # establish the connection between reddit and discord
    discord_side, reddit_side = mp.Pipe()

    # start the discord bot
    # the target is the function that runs the discord bot
    # the args are the arguments passed to the target function
    discord_process = mp.Process(target=discord_bot_go, args=[discord_side])
    discord_process.start()

    # start the reddit bot
    # the target is the function that runs the reddit bot
    # the args are the arguments passed to the target function
    reddit_process = mp.Process(target=reddit_bot_go, args=[reddit_side])
    reddit_process.start()
