import discord
from discord import app_commands
from discord.ext import commands

class PersonalColor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="personalcolor", description="add or update personal colored role")
    async def personal_color_assignment(self, interaction: discord.Interaction, 테마: str):
        role = discord.utils.get(interaction.guild.roles, name=interaction.user.name)

        if role:  # role is already there
            await role.edit(color=int(테마, 16))
        else:  # role is not in the list
            # new role
            role = await interaction.guild.create_role(name=interaction.user.name, color=int(테마, 16))

        # Build new role order
        # Start with all roles except the new one
        new_roles_order = [r for r in interaction.guild.roles]

        # Insert new role just above the 6th role
        target_index = 10
        new_roles_order.insert(target_index, role)
        print(new_roles_order)

        await interaction.guild.edit_role_positions(positions={role: i for i, role in enumerate(new_roles_order)})
        await interaction.user.add_roles(role)

        await interaction.response.send_message(f"퍼컬이 {테마}으로 변경되었습니다.", ephemeral=True)

    @app_commands.command(name="personalcolordelete", description="delete personal color role")
    async def personal_color_deletion(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=interaction.user.name)

        if role:
            await role.delete()
            await interaction.response.send_message("퍼스널 컬러가 삭제되었습니다.", ephemeral=True)
        else:
            await interaction.response.send_message("퍼스널 컬러가 존재하지 않습니다.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PersonalColor(bot))
