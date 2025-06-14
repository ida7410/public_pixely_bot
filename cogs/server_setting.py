import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import register_server, update_server, get_server_by_id
from typing import Literal
from config import lang

class ServerSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="server_register"
        , aliases=[entry["name"] for entry in lang["server_register"].values()])
    async def register_server_command(self, ctx: commands.Context):
        invoke = ctx.invoked_with
        local = ""
        if invoke == "register":
            local = "en"
        elif invoke == "채널등록":
            local = "ko"

        guild = ctx.guild
        if not guild:
            await ctx.send(lang["error"][local]["not_guild"])
            return

        if ctx.author.id != guild.owner_id:
            await ctx.send(lang["error"][local]["not_owner"])
            return

        success = register_server(guild.id, guild.owner_id)

        if success:
            print(lang["server_register"][local]["response"].format(server_name=guild.name))
            await ctx.send(lang["server_register"][local]["response"].format(server_name=guild.name))
        else:
            await ctx.send(lang["error"][local]["already_registered"])

    @commands.command(name="set_channel"
        , aliases=[entry["name"] for entry in lang["set_channel"].values()])
    async def set_channel(self, ctx: commands.Context, type_of: Literal['rule', 'role', 'youtube']
                                      , target_message_id: str):
        invoke = ctx.invoked_with
        local = ""
        if invoke == "setchannel" :
            local = "en"
        elif invoke == "채널등록" :
            local = "ko"


        guild = ctx.guild
        if not guild:
            await ctx.send(lang["error"][local]["not_guild"])
            return

        if ctx.author.id != guild.owner_id:
            await ctx.send(lang["error"][local]["not_owner"])
            return

        if not get_server_by_id(ctx.guild.id):
            await ctx.send(lang["error"][local]["not_registered"])
            return

        try:
            update_server(guild.id, guild.owner_id, type_of, int(target_message_id))
            await ctx.send(lang["set_channel"][local]["response"].format(server_name=guild.name))
        except Exception as e:
            await ctx.send(lang["error"][local]["update_failed"].format(e=e))

async def setup(bot):
    await bot.add_cog(ServerSetting(bot))