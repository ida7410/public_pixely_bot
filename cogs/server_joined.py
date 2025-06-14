import time

import discord
from discord.ext import commands

from config import lang_en, lang_ko

class ServerJoined(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild:discord.Guild):

        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            try:
                await guild.system_channel.send(view=Button())
                await guild.system_channel.send(lang_en["server_joined"]["greeting"][0].format(owner_name=guild.owner.name)
                                    + "\n" + lang_ko["server_joined"]["greeting"][0].format(owner_name=guild.owner.name))
                time.sleep(2)
                for i in range(0, len(lang_en["server_joined"]["greeting"])):
                    await guild.system_channel.send(lang_en["server_joined"]["greeting"][i].format(owner_name=guild.owner.name)
                                    + "\n" + lang_ko["server_joined"]["greeting"][i].format(owner_name=guild.owner.name))
                    time.sleep(2)
                return
            except Exception as e:
                print(f"sending message to system channel failed for {e}")


        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(lang_en["server_joined"]["greeting"][0].format(owner_name=guild.owner.name)
                                       + "\n" + lang_ko["server_joined"]["greeting"][0].format(owner_name=guild.owner.name))
                    time.sleep(2)
                    for i in range(0, len(lang_en["server_joined"]["greeting"])):
                        await channel.send(lang_en["server_joined"]["greeting"][i].format(owner_name=guild.owner.name)
                            + "\n" + lang_ko["server_joined"]["greeting"][i].format(owner_name=guild.owner.name))
                        time.sleep(2)
                    return
                except Exception as e:
                    print(f"sending message to system channel failed for {e}")

async def setup(bot):
    await bot.add_cog(ServerJoined(bot))
