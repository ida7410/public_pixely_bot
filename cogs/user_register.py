import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import register_user
from typing import Literal
from config import lang

class UserRegister(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userregister")
    async def register_server_command(self, ctx: commands.Context):
        # invoke = ctx.invoked_with
        local = "en"

        guild = ctx.guild
        if not guild:
            await ctx.send(lang["error"][local]["not_guild"])
            return

        if ctx.author.id != guild.owner_id:
            await ctx.send(lang["error"][local]["not_owner"])
            return

        success = register_user(ctx.author.id)

        if success:
            await ctx.send("user registered")
        else:
            await ctx.send("already registered user")

async def setup(bot):
    await bot.add_cog(UserRegister(bot))