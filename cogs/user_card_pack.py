from math import floor
from random import random, choices

import discord
from discord import app_commands
from discord.ext import commands, tasks

from cogs.card_pagination_view import CardPaginationView
from cogs.check import is_user_registered
from db.mongo import (user_collection, add_pack_user_by_user_discord_id, delete_pack_user_by_user_discord_id,
                      add_card_to_user_by_discord_id, get_cards_by_user_discord_id, get_user_by_user_discord_id,
                      get_cards_by_class, get_cards_by_class_member, get_card_by_id,
                      add_card_to_user_deck_by_discord_id,
                      get_cards_quantities_by_user_discord_id, drop_user_deck_by_user_discord_id,
                      get_user_deck_by_user_discord_id, get_user_deck_cards_id_by_user_discord_id,
                      get_card_quantity_by_user_discord_id_card_id)
from config import get_color

from datetime import timezone, timedelta, time

class UserCardPack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page = 1
        self.add_pack_at_zero.start()


    @tasks.loop(time=time(hour=00, minute=00, tzinfo=timezone(timedelta(hours=-4))))  # Create the task
    async def add_pack_at_zero(self):
        try:
            for user in user_collection.find():
                add_pack_user_by_user_discord_id(user.get("user_id"), ("all", "normal"))
                print("pack added to " + user.get("user_id", ""))
        except Exception as e:
            print(e)


    @app_commands.choices(type_name=[
        app_commands.Choice(name="라더", value="rather"),
        app_commands.Choice(name="덕개", value="duckgae"),
        app_commands.Choice(name="각별", value="heptagram"),
        app_commands.Choice(name="공룡", value="dino"),
        app_commands.Choice(name="잠뜰", value="sleepground"),
        app_commands.Choice(name="수현", value="suhyen"),
        app_commands.Choice(name="전체", value="all")
    ])
    @app_commands.choices(class_name=[
        app_commands.Choice(name="일반", value="normal"),
        app_commands.Choice(name="특급", value="special")
    ])
    @app_commands.command(name="addpack", description="add pack")
    async def add_pack(self, interaction: discord.Interaction, type_name: app_commands.Choice[str]
                       , class_name: app_commands.Choice[str]):
        try:
            add_pack_user_by_user_discord_id(interaction.user.id, (type_name.value, class_name.value))
        except Exception as e:
            print(e)

    @app_commands.command(name="getmypack", description="check my pack")
    @app_commands.check(is_user_registered)
    async def get_pack_command(self, interaction: discord.Interaction, ephemeral: bool = False):
        result = ""

        try :
            user = get_user_by_user_discord_id(interaction.user.id)
            user_pack = user.get("pack", "")
            for pack in user_pack:
                result += f'{pack.get("class", "")} pack of {pack.get("type", "")}\n'
            await interaction.response.send_message(result, ephemeral=ephemeral)
        except Exception as e:
            print(e)

    async def pack_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        user = get_user_by_user_discord_id(interaction.user.id)
        choices = []
        for pack in user["pack"]:
            pack_name = f"{pack['class']} - {pack['type']}"
            pack_value = f"{pack['class']}_{pack['type']}"
            choices.append(app_commands.Choice(name=pack_name, value=pack_value))
        return choices

    @app_commands.command(name="unpack", description="unpack")
    @app_commands.autocomplete(pack=pack_autocomplete)
    @app_commands.check(is_user_registered)
    async def unpack(self, interaction: discord.Interaction, pack: str):
        try:
            await interaction.response.send_message("카드를 뽑는 중...")
            class_name, type_name = pack.split("_")
            cards = self.get_card_unpack(interaction.user.id, type_name, class_name)
            embeds = []
            for card in cards:
                embeds.append(self.make_embed(card))
            await interaction.edit_original_response(content="", embeds=embeds)
            delete_pack_user_by_user_discord_id(interaction.user.id, (type_name, class_name))
        except Exception as e:
            print(e)

    def make_embed(self, card):
        color = get_color(card["member"])
        embed = discord.Embed(title=card["title"], description=f"**{card['desc']}**\n\n\" {card['line']} \"", color=color)
        return embed

    def get_card_unpack(self, user_id, type_name, class_name):
        possibility = ["normal", "rare", "special", "legend"]
        cards = []
        for i in range(5):
            cards_found = None
            if class_name == "normal":
                class_rand = choices(population=possibility, weights=[50, 30, 15, 5], k=1)[0]
                if type_name == "all":
                    cards_found = list(get_cards_by_class(str(class_rand)))
                    print(cards_found)
                else:
                    cards_found = list(get_cards_by_class_member(str(class_rand), type_name))

            if class_name != "normal":
                class_rand = choices(population=possibility, weights=[0, 0, 75, 25], k=1)[0]
                cards_found = list(get_cards_by_class(str(class_rand)))
                print(cards_found)

            total_cards = len(cards_found)

            card_rand_index = floor(random() * total_cards)
            card = cards_found[card_rand_index]
            add_card_to_user_by_discord_id(user_id, card["_id"])
            cards.append(card)
        return cards

    @app_commands.command(name="getmycards", description="get my cards")
    @app_commands.check(is_user_registered)
    async def get_my_cards(self, interaction: discord.Interaction, ephemeral: bool = True):
        await interaction.response.send_message("카드 가져오는 중")
        message = await interaction.original_response()
        cards = get_cards_by_user_discord_id(interaction.user.id)
        view = CardPaginationView()
        view.cards = cards
        view.user_name = interaction.user.name
        view.message = message
        await view.send_message(interaction)


async def setup(bot):
    await bot.add_cog(UserCardPack(bot))