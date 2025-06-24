import discord

from db.mongo import get_user_by_user_discord_id, get_game_by_id


def is_user_registered(interaction: discord.Interaction):
    if not get_user_by_user_discord_id(interaction.user.id):
        return False
    else:
        return True

def is_in_game(interaction: discord.Interaction):
    user = get_user_by_user_discord_id(interaction.user.id)
    if not user:
        return False

    if user["game"] == "":
        return False

    game = get_game_by_id(user)
    if not game:
        return False

    if game["thread_id"] != interaction.channel_id:
        print("Not int thread")
        return False

    return True