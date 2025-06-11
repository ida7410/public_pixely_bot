import discord
from discord import app_commands
from discord.ext import commands

class PrivateChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="createprivatechannel", description="create own private channel")
    async def create_private_channel(self, interaction: discord.Interaction,):
        if not discord.utils.get(interaction.guild.categories, name='personal-channel'):
            await interaction.guild.create_category(name="personal-channel")

        if discord.utils.get(interaction.guild.channels, name=interaction.user.name):
            await interaction.response.send_message(content="there exists personal channel already", ephemeral=False)
            return

        overwrite = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),  # hide from everyone
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),  # allow the user
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True)  # allow bot
        }
        await interaction.guild.create_text_channel(name=interaction.user.name
                                                    , category=discord.utils.get(interaction.guild.categories,
                                                                                 name='personal-channel')
                                                    , overwrites=overwrite)
        await interaction.response.send_message(content=f"{interaction.user.name}'s personal channel has been created", ephemeral=False)

async def setup(bot):
    await bot.add_cog(PrivateChannel(bot))
