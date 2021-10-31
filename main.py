from os import getenv
from sys import exit
import shelve
import secrets

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
        post = await channel.fetch_message(db["post"])
        raffle = int(db["raffle"])

        if raffle >= 312:
            exit(1)

        # tally up pumpkin reactions
        winner = ""
        winning_reaction = None
        for reaction in post.reactions:
            if bytes(str(reaction.emoji), "utf-8") == b"\xf0\x9f\x8e\x83":
                winning_reaction = reaction
                reactors = await reaction.users().flatten()
                try:
                    reactors.remove(client.user)
                except ValueError:
                    pass
                winner = secrets.choice(reactors)
                print(f"winner: {winner}")

        if winner:

            # edit post to show winner
            if raffle == 100:
                nft_type = "Legendary"
            elif (raffle > 100) and (raffle < 104):
                nft_type = "Epic"
            elif (raffle > 149) and (raffle < 161):
                nft_type = "Epic"
            elif (raffle > 229) and (raffle < 241):
                nft_type = "Epic"
            elif raffle == 312:
                nft_type = "Legendary"
            else:
                nfts = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
                nft_type = secrets.choices(
                    nfts, weights=(70, 18, 8, 3.5, 0.5), k=1
                ).pop()
            await post.edit(
                content=f'Raffle #{raffle}\n\n{getenv("TEXT")}\n\nCongratulations <@{str(winner.id)}>!\nYou won a {nft_type} NFT!'
            )
            print(f"winner posted: {nft_type}")

            # add winnder to log
            winners = await leaderboard_channel.fetch_message(db["winners"])
            winners_post = winners.content + f"\n#{raffle}. {str(winner)} | {nft_type}"
            try:
                await winners.edit(content=winners_post)
            except:
                leaderboard_post = await leaderboard_channel.send(
                    f"NFT Raffle Winners:\n#{raffle}. {str(winner)} | {nft_type}"
                )
                db["winners"] = leaderboard_post.id

            # update all the reactors scores
            try:
                scores = db["scores"]
            except KeyError:
                scores = {}

            for user in reactors:
                if str(user.id) == str(client.user.id):
                    continue
                scores[str(user)] = scores.get(str(user), 0) + 1
                print(f"updated score for {str(user)}: {scores[str(user)]}")

            # save scores
            db["scores"] = scores

            # update leaderboard
            if scores:
                leaderboard = await leaderboard_channel.fetch_message(db["leaderboard"])
                sorted_scores = {
                    k: v
                    for k, v in sorted(
                        scores.items(), key=lambda item: item[1], reverse=True
                    )
                }
                leaderboard_text = "Current Scores:\n\n"
                leaderboard_limit = 1
                for i in sorted_scores.keys():
                    if leaderboard_limit > 25:
                        break
                    leaderboard_text += (
                        f"{leaderboard_limit}. {i} | {sorted_scores[i]}\n"
                    )
                    leaderboard_limit += 1
                await leaderboard.edit(content=leaderboard_text)

        # post new message
        db["raffle"] = raffle + 1
        new_post = await channel.send(f"Raffle #{db['raffle']}\n\n" + getenv("TEXT"))
        db["post"] = new_post.id
        print(f"new post: {new_post.id}")
        if winning_reaction:
            await new_post.add_reaction(winning_reaction)

        db.close()
        exit(0)

    client.run(getenv("TOKEN"))
