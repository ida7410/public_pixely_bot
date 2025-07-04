import random

import discord
from discord import app_commands
from discord.ext import commands

from cogs.card_pagination_view import CardPaginationView
from cogs.check import is_user_registered, is_in_game
from config import get_color
from db.mongo import get_game_by_id_finished, get_user_by_user_discord_id, \
    update_game_player_deck_by_game_id_user_discord_id, get_user_deck_cards_id_by_user_discord_id, \
    update_game_drop_card_in_player_deck_hand_by_game_id_player_discord_id, \
    get_game_player_deck_by_game_id_user_discord_id, get_card_by_id, get_game_player_hand_by_game_id_user_discord_id, \
    get_game_by_id, update_game_player_hand_by_game_id_player_num, get_game_player_num_by_game_id_player_discord_id, \
    get_game_player_deck_by_game_id_player_num, update_game_player_deck_by_game_id_player_num


class CardDeck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="shuffle", description="make a game")
    @app_commands.check(is_user_registered)
    @app_commands.check(is_in_game)
    async def shuffle(self, interaction: discord.Interaction):
        await interaction.response.send_message("deck is being shuffled...", ephmeral=True)

        player_id = interaction.user.id
        deck_cards_id = get_user_deck_cards_id_by_user_discord_id(player_id)
        player = get_user_by_user_discord_id(player_id)
        game = get_game_by_id_finished(player["game"], False)

        random.shuffle(deck_cards_id)
        update_game_player_deck_by_game_id_user_discord_id(game["_id"], player_id, deck_cards_id, "shuffled")

        await interaction.edit_original_response(content="deck is now shuffled")

    def make_embed(self, card):
        color = get_color(card["member"])
        embed = discord.Embed(title=card["title"], description=f"**{card['desc']}**\n\n\" {card['line']} \"", color=color)
        return embed

    @app_commands.command(name="draw", description="draw a card")
    @app_commands.check(is_user_registered)
    @app_commands.check(is_in_game)
    async def draw(self, interaction: discord.Interaction, num_of_card: int = 1):
        msg = await interaction.channel.send("drawing a card...")
        await interaction.response.send_message("drawing a card...", ephemeral=True)

        player_id = interaction.user.id
        player = get_user_by_user_discord_id(player_id)
        game = get_game_by_id_finished(player["game"], False)
        player_num = get_game_player_num_by_game_id_player_discord_id(game["_id"], player_id)

        try:
            embeds = []
            for i in range(num_of_card):
                card_drawn = self.draw_card(game["_id"], player_num)
                new_deck = self.new_deck(game["_id"], player_num, card_drawn["_id"])
                update_game_player_deck_by_game_id_player_num(game["_id"], player_num, new_deck, "draw")
                update_game_player_hand_by_game_id_player_num(game["_id"], player_num, card_drawn["_id"], "draw")

                embeds.append(self.make_embed(card_drawn))
            await interaction.edit_original_response(content="", embeds=embeds)

            await msg.edit(content="drawing completed")
        except Exception as e:
            print(e)

    @app_commands.command(name="drawanother", description="draw a card")
    @app_commands.check(is_user_registered)
    @app_commands.check(is_in_game)
    async def draw_another_deck(self, interaction: discord.Interaction, num_of_card: int = 1):
        msg = await interaction.channel.send("drawing a card from another player's deck...")
        await interaction.response.send_message("drawing a card...", ephemeral=True)

        player_id = interaction.user.id
        player = get_user_by_user_discord_id(player_id)
        game = get_game_by_id_finished(player["game"], False)
        player_num = get_game_player_num_by_game_id_player_discord_id(game["_id"], player_id)
        if player_num == 1:
            another_player_num = 2
        else:
            another_player_num = 1

        try:
            embeds = []
            for i in range(num_of_card):
                card_drawn = self.draw_card(game["_id"], another_player_num)
                new_deck = self.new_deck(game["_id"], another_player_num, card_drawn["_id"])
                update_game_player_deck_by_game_id_player_num(game["_id"], another_player_num, new_deck, "draw")
                update_game_player_hand_by_game_id_player_num(game["_id"], player_num, card_drawn["_id"], "draw")

                embeds.append(self.make_embed(card_drawn))
            await interaction.edit_original_response(content="", embeds=embeds)

            await msg.edit(content="drawing completed")
        except Exception as e:
            print(e)

    @app_commands.command(name="copyanother", description="draw a card")
    @app_commands.check(is_user_registered)
    @app_commands.check(is_in_game)
    async def copy_another_deck(self, interaction: discord.Interaction, num_of_card: int = 1):
        msg = await interaction.channel.send("copying a card from another player's deck...")
        await interaction.response.send_message("copying a card...", ephemeral=True)

        player_id = interaction.user.id
        player = get_user_by_user_discord_id(player_id)
        game = get_game_by_id_finished(player["game"], False)
        player_num = get_game_player_num_by_game_id_player_discord_id(game["_id"], player_id)
        if player_num == 1:
            another_player_num = 2
        else:
            another_player_num = 1

        try:
            embeds = []
            for i in range(num_of_card):
                card_drawn = self.draw_card(game["_id"], another_player_num)
                update_game_player_hand_by_game_id_player_num(game["_id"], player_num, card_drawn["_id"], "draw")

                embeds.append(self.make_embed(card_drawn))
            await interaction.edit_original_response(content="", embeds=embeds)

            await msg.edit(content="drawing completed")
        except Exception as e:
            print(e)

    def draw_card(self, game_id, player_num):
        deck_cards_id = get_game_player_deck_by_game_id_player_num(game_id, player_num)
        rand_card_id = random.choice(deck_cards_id)
        card_drawn = get_card_by_id(rand_card_id)
        return card_drawn

    def new_deck(self, game_id, player_num, card_id):
        game = get_game_by_id(game_id)
        deck_cards_id = game[f"player{player_num}"]["deck"]
        index = deck_cards_id.index(card_id)
        new_deck = deck_cards_id[:index]
        new_deck.extend(deck_cards_id[index + 1:])
        return new_deck


    @app_commands.command(name="getcardinmyhand", description="get card in hand")
    @app_commands.check(is_user_registered)
    @app_commands.check(is_in_game)
    async def get_hand(self, interaction: discord.Interaction, sep: int = 9):
        try:
            await interaction.response.send_message("덱을 가져오는 중...")
            message = await interaction.original_response()
            game = get_game_by_id(get_user_by_user_discord_id(interaction.user.id)["game"])
            deck_cards_id = get_game_player_hand_by_game_id_user_discord_id(game["_id"], interaction.user.id)
            cards = []
            for deck_card_id in deck_cards_id:
                card = get_card_by_id(deck_card_id)
                cards.append(card)

            view = CardPaginationView(sep)
            view.cards = cards
            view.user_name = interaction.user.name
            view.message = message
            await view.send_message(interaction)
        except Exception as e:
            print(e)

    async def card_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        player1 = get_user_by_user_discord_id(interaction.user.id)
        hand = get_game_player_hand_by_game_id_user_discord_id(player1["game"], player1["discord_id"])
        choices = []
        for card_id in hand["pack"]:
            card_name = get_card_by_id(card_id)["title"]
            card_value = card_id
            choices.append(app_commands.Choice(name=card_name, value=card_value))
        return choices

    @app_commands.command(name="drop", description="unpack")
    @app_commands.autocomplete(card=card_autocomplete)
    @app_commands.check(is_user_registered)
    @app_commands.check(is_in_game)
    async def drop(self, interaction: discord.Interaction, card: str):
        try:
            await interaction.response.send_message("dropping card...")
            embed = self.make_embed(get_card_by_id(card))
            game = get_game_by_id(get_user_by_user_discord_id(interaction.user.id)["game"])
            player_num = get_game_player_num_by_game_id_player_discord_id(game["_id"], interaction.user.id)
            update_game_player_hand_by_game_id_player_num(game["_id"], player_num, card, "drop")
            await interaction.edit_original_response(content="", embed=embed)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(CardDeck(bot))
