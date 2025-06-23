import discord
from discord import app_commands
from discord.ext import commands

from cogs.check import is_user_registered
from db.mongo import (insert_game, update_game_hp_by_game_id_player_num, get_card_by_title,
                      get_games_by_user_discord_id, update_game_finished_by_game_id,
                      update_user_game_by_user_discord_id,
                      get_user_deck_cards_id_by_user_discord_id, get_user_by_user_discord_id, get_game_by_id,
                      get_game_player_num_by_game_id_player_discord_id)


class GameHp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="edithp", description="stop game")
    @app_commands.check(is_user_registered)
    async def edit_hp(self, interaction: discord.Interaction, hp: int):
        try:
            await interaction.response.send_message("editting hp...")
            game = get_game_by_id(get_user_by_user_discord_id(interaction.user.id)["game"])
            if not game:
                await interaction.edit_original_response(content="there is no game proceeding")
                return

            player_num = get_game_player_num_by_game_id_player_discord_id(game["_id"], interaction.user.id)
            update_game_hp_by_game_id_player_num(game["_id"], player_num, hp, f"player {player_num}: hp {hp}")

            if interaction.guild.owner_id != interaction.user.id:
                original_nick = interaction.user.nick
                if "| HP " in original_nick:
                    original_nick_arr = original_nick.split("| HP")
                    new_nick = original_nick_arr[0]
                else:
                    new_nick = interaction.user.nick

                new_nick += "| HP " + str(game[f"player{player_num}"]["hp"] + hp)
                await interaction.user.edit(nick=new_nick)

            await interaction.edit_original_response(content=f"player {player_num} hp changed by {hp}")
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(GameHp(bot))
