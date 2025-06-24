from math import floor
from random import random, choices

import discord
from bson import ObjectId
from discord import app_commands, Object
from discord.ext import commands, tasks

from cogs.card_pagination_view import CardPaginationView
from cogs.check import is_user_registered
from db.mongo import (get_card_by_id, add_card_to_user_deck_by_discord_id, get_user_deck_cards_id_by_user_discord_id,
                      get_cards_quantities_by_user_discord_id, drop_user_deck_by_user_discord_id,
                      get_card_quantity_by_user_discord_id_card_id)
from config import get_color


class UserCardDeck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page = 1

    def make_embed(self, card):
        color = get_color(card["member"])
        embed = discord.Embed(title=card["title"], description=f"**{card['desc']}**\n\n\" {card['line']} \"", color=color)
        return embed

    @app_commands.choices(class_name=[
        app_commands.Choice(name="일반", value="normal"),
        app_commands.Choice(name="특급", value="special")
    ])
    @app_commands.choices(member=[
        app_commands.Choice(name="라더", value="rather"),
        app_commands.Choice(name="덕개", value="duckgae"),
        app_commands.Choice(name="각별", value="heptagram"),
        app_commands.Choice(name="공룡", value="dino"),
        app_commands.Choice(name="잠뜰", value="sleepground"),
        app_commands.Choice(name="수현", value="suhyen")
    ])
    @app_commands.command(name="insertdeckby", description="insert cards in the order of")
    @app_commands.check(is_user_registered)
    async def insert_deck(self, interaction: discord.Interaction, class_name: app_commands.Choice[str] = None
                           , member: app_commands.Choice[str] = None):
        await interaction.response.send_message("setting deck...", ephemeral=True)

        drop_user_deck_by_user_discord_id(interaction.user.id)

        cards_found = get_cards_quantities_by_user_discord_id(interaction.user.id)
        cards = []
        if class_name is not None and class_name.value == "special":
            for card in cards_found:
                class_found = get_card_by_id(card["card_id"])["class"]
                if class_found == "special" or class_found == "legend":
                    cards.append(card)
            cards_found = cards.copy()

        if member is not None:
            cards = []
            for card in cards_found:
                if member.value == get_card_by_id(card["card_id"])["member"]:
                    cards.append(card)
            cards_found = cards.copy()

        count_cards = 0
        try:
            for index, card in enumerate(cards_found):
                quantity_found = cards_found[index]["quantity"]
                while quantity_found > 0 and count_cards <= 25:
                    cards.append(card)
                    add_card_to_user_deck_by_discord_id(interaction.user.id, card["card_id"])
                    quantity_found -= 1
                    count_cards += 1
        except Exception as e:
            print(e)

        await interaction.edit_original_response(content="deck setting is done")

    async def card_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        user = get_user_by_user_discord_id(interaction.user.id)
        choices = []
        for card_id_quantity in user["cards"]:
            card = get_card_by_id(card_id_quantity["card_id"])
            card_name = f"{card['title']}"
            card_value = f"{card['_id']}"
            choices.append(app_commands.Choice(name=card_name, value=card_value))
        return choices

    async def card_quantity_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        try:
            choices = []
            quantity = get_card_quantity_by_user_discord_id_card_id(interaction.user.id, ObjectId(interaction.namespace.card))
            deck = get_user_deck_cards_id_by_user_discord_id(interaction.user.id)
            quantity -= deck.count(ObjectId(interaction.namespace.card))

            for i in range(quantity):
                quantity_name = str(quantity)
                quantity_value = quantity
                choices.append(app_commands.Choice(name=quantity_name, value=quantity_value))

            if quantity == 0:
                choices.append(app_commands.Choice(name="0", value=0))
            return choices
        except Exception as e:
            print(e)

    @app_commands.command(name="insertcardtodeck", description="insert cards in the order of")
    @app_commands.autocomplete(card=card_autocomplete)
    @app_commands.autocomplete(quantity=card_quantity_autocomplete)
    @app_commands.check(is_user_registered)
    async def insert_card_to_deck(self, interaction: discord.Interaction, card: str, quantity: int):
        await interaction.response.send_message("adding card to deck...", ephemeral=True)

        count_cards = len(get_user_deck_cards_id_by_user_discord_id(interaction.user.id))
        try:
            while quantity > 0 and count_cards <= 25:
                add_card_to_user_deck_by_discord_id(interaction.user.id, ObjectId(card))
                quantity -= 1
                count_cards += 1
        except Exception as e:
            print(e)

        await interaction.edit_original_response(content="deck setting is done")

    @app_commands.command(name="dropdeck", description="drop deck")
    @app_commands.check(is_user_registered)
    async def drop_deck(self, interaction: discord.Interaction):
        await interaction.response.send_message("dropping deck...", ephemeral=True)
        drop_user_deck_by_user_discord_id(interaction.user.id)
        await interaction.edit_original_response(content="deck is now empty")

    @app_commands.command(name="getmydeck", description="get deck")
    @app_commands.check(is_user_registered)
    async def get_deck(self, interaction: discord.Interaction):
        try:
            await interaction.response.send_message("덱을 가져오는 중...", ephemeral=True)
            message = await interaction.original_response()
            deck_cards_id = get_user_deck_cards_id_by_user_discord_id(interaction.user.id)
            cards = []
            for deck_card_id in deck_cards_id:
                card = get_card_by_id(deck_card_id)
                cards.append(card)

            view = CardPaginationView()
            view.cards = cards
            view.user_name = interaction.user.name
            view.message = message
            await view.send_message(interaction)
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(UserCardDeck(bot))