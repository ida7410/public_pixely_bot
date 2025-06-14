import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import insert_card
from typing import Literal
from config import lang

class InsertCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.static_id = 0

    @app_commands.command(name="insertcard", description="카드 등록용")
    @app_commands.choices(member=[
        app_commands.Choice(name="라더", value="rather"),
        app_commands.Choice(name="덕개", value="duckgae"),
        app_commands.Choice(name="각별", value="heptagram"),
        app_commands.Choice(name="공룡", value="dino"),
        app_commands.Choice(name="잠뜰", value="sleepground"),
        app_commands.Choice(name="수현", value="suhyen")
    ])
    async def register_server_command(self, interaction: discord.Interaction, member: app_commands.Choice[str],
                                        title: str, line:str, desc: str):

        insert_card(self.static_id, str(member), title, line, desc)
        await interaction.response.send_message(f"카드가 등록되었습니다!\nid:{self.static_id} | member:{member}"
                    f"\n**\" {title}** \"\n{line}\n```{desc}```")

        self.static_id += 1

async def setup(bot):
    await bot.add_cog(InsertCard(bot))
