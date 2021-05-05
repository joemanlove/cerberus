# reddit_bot module for use with cerberus
# written by Joe Manlove
# created March 2021
# forked 4/25-27 2021

"""
reddit_bot provides the discord integration for cerberus.

User settings should be included in the reddit_config file.

Only the function reddit_bot_go is intended for import.

Expected use:
-------------
from reddit_bot import reddit_bot_go
"""

# tools for interacting with reddit
import praw

# import settings from file
from config import reddit_config

# initialize with appropriate values
client_id = reddit_config["client_id"]
client_secret = reddit_config["client_secret"]
username = reddit_config["username"]
password = reddit_config["password"]
user_agent = reddit_config["user_agent"]

# creating an authorized reddit instance
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=username,
                     password=password,
                     user_agent=user_agent)

# Only allow bot to engage with private subreddit.
subreddit = reddit.subreddit('mechanicalMercs')

class Message_for_Discord:
    """
    Message_for_Discord, a wrapper for Discord messages.

    Attributes
    ----------
    title : str
        the title of the message
    text : str
        the body of the message
    """
    def __init__(self, title, text=" "):
        """
        Initializes a message to be sent to the discord bot.

        Parameters
        ----------
        title : str
            the title of the message
        text : str, optional
            the body of the message (default is " ")
        """
        self.title = title
        self.text = text

def reddit_bot_go(connection):
    """
    Make the reddit bot go brrrr....

    Infinite loop - checks for messages from Discord bot, check for new submissions to parse, repeat

    Parameters
    ----------
    reddit_connection
        half of a Pipe (multiprocessing) connecting the reddit process and the discord process
    """
    # Initialize streams, pause_after=-1 stops blocking after a batch of messages
    comment_stream = subreddit.stream.comments(pause_after=-1, skip_existing=True)
    submission_stream = subreddit.stream.submissions(pause_after=-1, skip_existing=True)
    print("Reddit bot ready...")
    # main looop
    while True:
        # Process messages from the Discord Bot
        if connection.poll():
            msg = connection.recv()
            subreddit.submit(msg.title, selftext=msg.text)

        # For new submissions to the subreddit
        for submission in submission_stream:

            # break after the end of the current batch
            if submission is None:
                break

            if submission.selftext:
                print(f"Processing a submission with id {submission.id}.")
                text = submission.selftext

                # if the text contains the word 'discord'
                if text.count("discord"):
                    msg = Message_for_Discord(submission.title, text)
                    connection.send(msg)
                    print("Sending to Discord")
                    submission.reply("Crossposted to Discord.")

        # For new comments to the subreddit
        for comment in comment_stream:

            # break after the end of the current batch
            if comment is None:
                break

            if comment.body:
                print(f"Processing a comment with id {comment.id}.")

                # if the text contains the word 'discord'
                if comment.body.count("discord"):
                    msg = Message_for_Discord(comment.submission.title, comment.submission.selftext)
                    connection.send(msg)
                    print("Sending to Discord")
                    comment.reply("Crossposted to original submission to Discord.")
