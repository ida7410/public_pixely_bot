from math import floor
from random import random, choices
from xml.sax.saxutils import escape

import discord
from discord import app_commands, Color
from discord.ext import commands, tasks
from discord.ext.commands import ColorConverter

from cogs.card_pagination_view import CardPaginationView
from db.mongo import register_user, get_user_by_user_id, user_collection, add_pack_user, delete_pack_user, \
    card_collection, add_card_to_user, get_cards_by_user_id, get_card_by_id
from typing import Literal
from config import lang, get_color

import datetime
from datetime import timezone, timedelta, time

class UserRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.page = 1
        self.add_pack_at_zero.start()


    @app_commands.command(name="userregister", description="register user")
    async def register_server_command(self, interaction: discord.Interaction):
        # invoke = ctx.invoked_with
        local = "en"

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(lang["error"][local]["not_guild"])
            return

        user_insert_success = register_user(interaction.user.id, ("all", "normal"))

        if user_insert_success:
            await interaction.response.send_message("user registered")
        else:
            await interaction.response.send_message("already registered user")

    @app_commands.command(name="getmypack", description="check my pack")
    async def get_pack_command(self, interaction: discord.Interaction):
        result = ""

        try :
            user = get_user_by_user_id(interaction.user.id)
            user_pack = user.get("pack", "")
            for pack in user_pack:
                result += f'{pack.get("class", "")} pack of {pack.get("type", "")}\n'
            await interaction.response.send_message(result)
        except Exception as e:
            print(e)

    @tasks.loop(time=time(hour=00, minute=00, tzinfo=timezone(timedelta(hours=-4))))  # Create the task
    async def add_pack_at_zero(self):
        try:
            for user in user_collection.find():
                add_pack_user(user.get("user_id"), ("all", "normal"))
                print("pack added to " + user.get("user_id", ""))
        except Exception as e:
            print(e)

    async def pack_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        user = user_collection.find_one({"user_id": interaction.user.id})
        choices = []
        for pack in user["pack"]:
            pack_name = f"{pack['class']} - {pack['type']}"
            pack_value = f"{pack['class']}_{pack['type']}"
            choices.append(app_commands.Choice(name=pack_name, value=pack_value))
        return choices

    @app_commands.command(name="unpack", description="unpack")
    @app_commands.autocomplete(pack=pack_autocomplete)
    async def unpack(self, interaction: discord.Interaction, pack: str):
        try:
            await interaction.response.send_message("카드를 뽑는 중...")
            class_name, type_name = pack.split("_")
            cards = self.get_card_unpack(interaction.user.id, type_name, class_name)
            embeds = []
            for card in cards:
                embeds.append(self.make_embed(card))
            await interaction.edit_original_response(content="", embeds=embeds)
            delete_pack_user(interaction.user.id, (type_name, class_name))
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
                    cards_found = list(card_collection.find({"class": str(class_rand)}))
                    print(cards_found)
                else:
                    cards_found = list(card_collection.find({"class": class_rand, "member": type_name}))

            if class_name != "normal":
                class_rand = choices(population=possibility, weights=[0, 0, 75, 25], k=1)[0]
                cards_found = list(card_collection.find({"class": str(class_rand)}))
                print(cards_found)

            total_cards = len(cards_found)

            card_rand_index = floor(random() * total_cards)
            card = cards_found[card_rand_index]
            add_card_to_user(user_id, card["_id"])
            cards.append(card)
        return cards

    @app_commands.command(name="getcards", description="unpack")
    async def get_my_cards(self, interaction: discord.Interaction):
        await interaction.response.send_message("```finding cards...```")
        message = await interaction.original_response()
        cards = get_cards_by_user_id(interaction.user.id)
        view = CardPaginationView()
        view.cards = cards
        view.user_name = interaction.user.name
        view.message = message
        await view.send_message(interaction)

        # try:
        #     if len(cards_copy) % 3 == 1:
        #         embed.add_field(name=" ", value=" ", inline=True)
        #     if len(cards_copy) % 3 == 2:
        #         embed.add_field(name=" ", value=" ", inline=True)
        #         embed.add_field(name=" ", value=" ", inline=True)
        # except Exception as e:
        #     print(e)

        # await interaction.response.send_message(embed=embed)


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
            add_pack_user(interaction.user.id, (type_name.value, class_name.value))
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(UserRegister(bot))