from math import floor

import discord
from discord import app_commands
from discord.ext import commands

from db.mongo import insert_card, card_collection
from typing import Literal
from config import lang

class InsertCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="insertcard", description="카드 등록용")
    @app_commands.choices(member=[
        app_commands.Choice(name="라더", value="rather"),
        app_commands.Choice(name="덕개", value="duckgae"),
        app_commands.Choice(name="각별", value="heptagram"),
        app_commands.Choice(name="공룡", value="dino"),
        app_commands.Choice(name="잠뜰", value="sleepground"),
        app_commands.Choice(name="수현", value="suhyen")
    ])
    @app_commands.choices(classes=[
        app_commands.Choice(name="일반", value="normal"),
        app_commands.Choice(name="희귀", value="rare"),
        app_commands.Choice(name="특급", value="special"),
        app_commands.Choice(name="전설", value="legend")
    ])
    async def insert_card(self, interaction: discord.Interaction, member: app_commands.Choice[str],
                          classes: app_commands.Choice[str], title: str, desc: str, line:str):
        desc = desc.replace('\\n', "\n")
        try:
            insert_card(member.value, classes.value, title, line, desc)
            await interaction.response.send_message(f"카드가 등록되었습니다!\nmember: {member.value} | class: {classes.value}"
                    f"\n# \" {title} \"\n\n{desc}\n\n```{line}```")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(InsertCard(bot))
