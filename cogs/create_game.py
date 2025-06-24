import discord
from discord import app_commands
from discord.ext import commands

from cogs.check import is_user_registered
from db.mongo import (insert_game, update_game_hp_by_game_id_player_num, get_card_by_title,
    get_games_by_user_discord_id, update_game_finished_by_game_id, update_user_game_by_user_discord_id,
    get_user_deck_cards_id_by_user_discord_id, get_user_by_user_discord_id, get_game_by_id)


class CreateGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="creategame", description="make a game")
    @app_commands.check(is_user_registered)
    async def create_game(self, interaction: discord.Interaction, member: discord.Member, hp: int = 10):
        await interaction.response.send_message("creating game...")

        player1_id = interaction.user.id
        player2_id = member.id

        # player1 = get_user_by_user_discord_id(player1_id)
        # game = player1["game"]
        # playing_other_game = (get_game_by_id(game) or
        #                       get_user_by_user_discord_id(player2_id)["game"])
        #
        # if playing_other_game:
        #     await interaction.edit_original_response(content="one of the players is still proceeding a game")
        #     return

        thread = interaction.guild.get_thread(interaction.channel_id)
        if thread is None:
            await interaction.edit_original_response(content="Game should proceed in thread")
            return

        if member not in await thread.fetch_members():
            await thread.add_user(member)

        try:
            await thread.join()

            player1_deck = get_user_deck_cards_id_by_user_discord_id(player1_id)
            player2_deck = get_user_deck_cards_id_by_user_discord_id(player2_id)
            inserted_game_id = insert_game(interaction.channel_id, player1_id, player1_deck, player2_id, player2_deck, hp)

            update_user_game_by_user_discord_id(player1_id, inserted_game_id)
            update_user_game_by_user_discord_id(player2_id, inserted_game_id)

            if get_card_by_title("투리")["_id"] in player1_deck:
                update_game_hp_by_game_id_player_num(inserted_game_id, 1, 3, "p1: hp + 3")

            if get_card_by_title("투리")["_id"] in player2_deck:
                update_game_hp_by_game_id_player_num(inserted_game_id, 2, 3, "p2: hp + 3")

            if interaction.guild.owner_id != interaction.user.id:
                await interaction.user.edit(
                    nick=f"{interaction.user.nick if interaction.user.nick is not None else interaction.user.name} "
                    f"| HP {get_game_by_id(inserted_game_id)['player1']['hp']}")
            if interaction.guild.owner_id != member.id:
                await member.edit(nick=f"{member.nick if member.nick is not None else member.name} | HP "
                                       f"{get_game_by_id(inserted_game_id)['player2']['hp']}")

            await interaction.edit_original_response(content="game has been created!")
        except Exception as e:
            print(e)

    async def game_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        games = get_games_by_user_discord_id(interaction.user.id)
        choices = []
        for game in games:
            player1_name = self.bot.get_guild(interaction.guild.id).get_member(game["player1"]["discord_id"]).name
            player2_name = self.bot.get_guild(interaction.guild.id).get_member(game["player2"]["discord_id"]).name

            game_name = f"{player1_name}_{player2_name} game"
            game_value = str(game["_id"])

            choices.append(app_commands.Choice(name=game_name, value=game_value))
        return choices

    @app_commands.command(name="stopgame", description="stop game")
    @app_commands.check(is_user_registered)
    async def stop_game(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("stopping game...")
            game = get_game_by_id(get_user_by_user_discord_id(interaction.user.id)["game"])
            if not game:
                await interaction.edit_original_response(content="there is no game proceeding")
                return

            update_game_finished_by_game_id(game["_id"])
            update_user_game_by_user_discord_id(get_user_by_user_discord_id(game["player1"]["discord_id"]), "")
            update_user_game_by_user_discord_id(get_user_by_user_discord_id(game["player2"]["discord_id"]), "")

            player1 = interaction.guild.get_member(game["player1"]["discord_id"])
            if player1.id != interaction.guild.owner_id:
                await player1.edit(nick=player1.nick.split(" |")[0])
            player2 = interaction.guild.get_member(game["player2"]["discord_id"])
            if player2.id != interaction.guild.owner_id:
                await player2.edit(nick=player1.nick.split(" |")[0])

            await interaction.response.send_message("game stopped")
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(CreateGame(bot))
