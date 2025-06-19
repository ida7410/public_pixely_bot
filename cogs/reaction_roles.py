import discord
from discord.ext import commands
from config import TARGET_EMOJI_PIXELY, TARGET_EMOJI_EX
from db.mongo import get_server_by_server_id


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        target_server = get_server_by_server_id(payload.guild_id)
        if not target_server :
            return

        # Check if the reaction is in the correct channel
        target_role_message_id = target_server.get("target_role_message_id", "")
        if payload.message_id != target_role_message_id:
            return

        # Check if the correct emoji was used
        if (str(payload.emoji.name) not in TARGET_EMOJI_PIXELY.keys()
                and str(payload.emoji.name) not in TARGET_EMOJI_EX.keys()):
            return

        # Get the guild, member, and role
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        if str(payload.emoji.name) in TARGET_EMOJI_PIXELY.keys() or str(payload.emoji.name):
            # Get the role
            role_name = TARGET_EMOJI_PIXELY.get(str(payload.emoji.name))
            role = discord.utils.get(guild.roles, name=role_name)
            if role is None:
                print(f"role '{role_name}' not found")
                return

            # Add the role to the user
            try:
                await member.add_roles(role)
                print(f"role is added '{role_name}' to {member.display_name}")
            except discord.Forbidden:
                print("missing permissions to add/remove role")
            except Exception as e:
                print(f"failed to add role: {e}")
        else:
            channel = discord.utils.get(guild.channels, name=TARGET_EMOJI_EX.get(payload.emoji.name))
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = False
            overwrite.read_messages = True
            await channel.set_permissions(member, overwrite=overwrite)
            print(f"{member} now can see {TARGET_EMOJI_EX.get(payload.emoji.name)}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        target_server = get_server_by_server_id(payload.guild_id)
        if not target_server:
            return

        # Check if the reaction is in the correct channel
        target_role_message_id = target_server.get("target_role_message_id", "")
        if payload.message_id != target_role_message_id:
            return

        # Check if the correct emoji was used
        if (str(payload.emoji.name) not in TARGET_EMOJI_PIXELY.keys()
                and str(payload.emoji.name) not in TARGET_EMOJI_EX.keys()):
            return

        # Get the guild, member, and role
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot:
            return

        # Get the role
        role_name = TARGET_EMOJI_PIXELY.get(str(payload.emoji.name))
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            print(f"role '{role_name}' not found")
            return

        # Remove the role to the user
        try:
            await member.remove_roles(role)
            print(f"role '{role_name}' is moved from {member.display_name}")
        except discord.Forbidden:
            print("missing permissions to add/remove role.")
        except Exception as e:
            print(f"Failed to add role: {e}")

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
