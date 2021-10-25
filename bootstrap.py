from os import getenv
from sys import exit
import shelve

import discord


if __name__ == "__main__":

    client = discord.Client()

    @client.event
    async def on_ready():

        # init database
        db = shelve.open("state")

        # get channel and post
        channel = client.get_channel(int(getenv("CHANNEL")))
        leaderboard_channel = client.get_channel(int(getenv("LEADERBOARD_CHANNEL")))

        # make inital leaderboard post
        leaderboard_post = await leaderboard_channel.send("NFT Raffle Winners:")
        db["winners"] = leaderboard_post.id

        # init first raffle
        # db["raffle"] = 1

        # Make inital post
        # new_post = await channel.send(f"Raffle #1\n\n" + getenv("TEXT"))
        # db["post"] = new_post.id

        # empty scoreboard
        # db["scores"] = {}

        db.close()
        exit(0)

    client.run(getenv("TOKEN"))
