import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import register_user
from typing import Literal
from config import lang

class UserRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userregister", description="register user")
    async def register_server_command(self, interaction: discord.Interaction):
        # invoke = ctx.invoked_with
        local = "en"

        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(lang["error"][local]["not_guild"])
            return

        success = register_user(interaction.user.id)

        if success:
            await interaction.response.send_message("user registered")
        else:
            await interaction.response.send_message("already registered user")

async def setup(bot):
    await bot.add_cog(UserRegister(bot))