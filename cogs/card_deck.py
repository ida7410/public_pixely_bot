import random

import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import get_game_by_id_finished, get_user_by_user_discord_id, \
    update_game_player_deck_by_game_id_user_discord_id, get_user_deck_cards_id_by_user_discord_id


class CardDeck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shuffle", description="make a game")
    async def shuffle(self, interaction: discord.Interaction):
        await interaction.response.send_message("deck is being shuffled...")

        player_id = interaction.user.id
        deck_cards_id = get_user_deck_cards_id_by_user_discord_id(player_id)
        player = get_user_by_user_discord_id(player_id)
        game = get_game_by_id_finished(player["game"], False)

        random.shuffle(deck_cards_id)
        update_game_player_deck_by_game_id_user_discord_id(game["_id"], player_id, deck_cards_id,
                                        f"player {interaction.user.name} deck shuffled")

        await interaction.edit_original_response(content="deck is now shuffled")

async def setup(bot):
    await bot.add_cog(CardDeck(bot))
