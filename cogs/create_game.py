import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import insert_game, get_user_deck_by_user_discord_id, update_game_hp_by_game_id_player_num, \
    is_target_card_id_in_deck, get_card_by_title, get_games_by_user_discord_id, update_game_finished_by_game_id, \
    update_user_game_by_user_discord_id, get_user_deck_cards_id_by_user_discord_id


class CreateGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="creategame", description="make a game")
    async def create_game(self, interaction: discord.Interaction, member: discord.Member, hp: int = 10):
        await interaction.response.send_message("creating game...")

        player1_id = interaction.user.id
        player2_id = member.id
        player1_deck = get_user_deck_cards_id_by_user_discord_id(player1_id)
        player2_deck = get_user_deck_cards_id_by_user_discord_id(player2_id)
        inserted_game_id = insert_game(player1_id, player1_deck, player2_id, player2_deck, hp)

        update_user_game_by_user_discord_id(player1_id, inserted_game_id)
        update_user_game_by_user_discord_id(player2_id, inserted_game_id)

        if get_card_by_title("투리")["_id"] in player1_deck:
            update_game_hp_by_game_id_player_num(inserted_game_id, 1, 3, "p1: hp + 3")

        if get_card_by_title("투리")["_id"] in player2_deck:
            update_game_hp_by_game_id_player_num(inserted_game_id, 2, 3, "p2: hp + 3")

        await interaction.edit_original_response(content="game has been created!")

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
    @app_commands.autocomplete(game=game_autocomplete)
    async def stop_game(self, interaction: discord.Interaction, game: str):
        try:
            update_game_finished_by_game_id(str(game))
            await interaction.response.send_message("game stopped")
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(CreateGame(bot))
