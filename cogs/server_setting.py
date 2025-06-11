import discord
from discord import app_commands
from discord.ext import commands
from db.mongo import register_server, update_server, get_server_by_id
from typing import Literal

class ServerSetting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="registerserver", description="register server (required)")
    async def register_server_command(self, ctx: commands.Context):
        guild = ctx.guild
        if not guild:
            await ctx.send("this command can be used only in the guild/server", ephemeral=False)
            return

        if ctx.author.id != guild.owner_id:
            await ctx.send("only owner can use this command", ephemeral=False)
            return

        success = register_server(guild.id, guild.owner_id)

        if success:
            await ctx.send(f"server **{guild.name}**(id: `{guild.id}`) has been registered", ephemeral=True)
            await ctx.send("you can proceed with server settings please take a look !help")
        else:
            await ctx.send("this server has already been registered", ephemeral=False)

    @commands.command(name="setmessage", description="set up message ids for pixely servers")
    async def register_server_command(self, ctx: commands.Context, type_of: Literal['rule', 'role', 'youtube']
                                      , target_message_id: str):
        guild = ctx.guild
        if not guild:
            await ctx.send("this command can be used only in the guild/server", ephemeral=False)
            return

        if ctx.author.id != guild.owner_id:
            await ctx.send("only owner can use this command", ephemeral=False)
            return

        if not get_server_by_id(ctx.guild.id):
            await ctx.send("server has not been registered")
            return

        try:
            update_server(guild.id, guild.owner_id, type_of, int(target_message_id))
            await ctx.send(f"server **{guild.name}**(id: `{guild.id}`) has been updated for"
                           f" {type_of} with message id of {target_message_id}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"updated failed : {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(ServerSetting(bot))
