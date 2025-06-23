import discord

from db.mongo import get_user_by_user_discord_id


def is_user_registered(interaction: discord.Interaction):
    if not get_user_by_user_discord_id(interaction.user.id):
        return False
    else:
        return True