from xml.sax.saxutils import escape

import discord
from discord import app_commands
from discord.ext import commands, tasks

from db.mongo import register_user, get_user_by_user_id, user_collection, add_pack_user
from typing import Literal
from config import lang

import datetime
from datetime import timezone, timedelta, time

class UserRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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


async def setup(bot):
    await bot.add_cog(UserRegister(bot))