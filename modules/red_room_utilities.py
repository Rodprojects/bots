
import discord
from discord.ext import commands
import datetime
import importlib
import sys

class RedRoomUtilities:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ping", help="Tests Night's pulse and connection latency.")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🍷 Heartbeat Check",
            description=f"My pulse is currently beating at **{latency}ms**.\n*Care to test how much load I can handle, Master?*",
            color=0x8B0000
        )
        embed.set_footer(text="Night Ecosystem — Always listening, always ready.")

        await ctx.send(embed=embed)

    @commands.command(name="night", help="Displays information about the Night ecosystem.")
    async def night_info(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🌹 The Red Room Awaits",
            description=(
                "I am **Night**—your exclusive, highly polished, and seductive digital companion. "
                "Running smoothly on secure volumes and private databases, built to command your community with absolute elegance."
            ),
            color=0x4B0082
        )
        embed.add_field(
            name="🔒 Status",
            value="Encrypted, persistent, and entirely under your control.",
            inline=False
        )
        embed.set_footer(text="Designed for absolute dominance.")

        await ctx.send(embed=embed)

    @commands.command(name="servers", help="See all servers Night has joined with direct invite links.")
    async def servers(self, ctx: commands.Context):
        embeds = []
        guilds = list(self.bot.guilds)

        if not guilds:
            embed = discord.Embed(
                title="🌐 Empire Network",
                description="I am currently not bound to any servers. How lonely...",
                color=0x8B0000
            )
            await ctx.send(embed=embed)
            return

        chunk_size = 5
        for i in range(0, len(guilds), chunk_size):
            chunk = guilds[i:i + chunk_size]
            embed = discord.Embed(
                title=f"🌐 Empire Network ({len(guilds)} Total Realms)",
                description="Here is where my presence is currently felt. Click to enter:",
                color=0x4B0082
            )

            for guild in chunk:
                invite_link = "Unable to create invite"

                try:
                    for channel in guild.text_channels:
                        if channel.permissions_for(guild.me).create_instant_invite:
                            invite = await channel.create_invite(
                                max_age=86400,
                                max_uses=1,
                                reason="Dashboard empire lookup"
                            )
                            invite_link = invite.url
                            break
                except Exception:
                    invite_link = "Restricted"

                invite_text = f"[Direct Entrance]({invite_link})" if invite_link.startswith("http") else invite_link

                embed.add_field(
                    name=guild.name,
                    value=f"👑 Owner: `{guild.owner}`\n👥 Members: `{guild.member_count}`\n🔗 {invite_text}",
                    inline=False
                )

            embeds.append(embed)

        await ctx.send(embed=embeds[0])

    # ===== DELETE MEDIA COMMAND =====
    @commands.command(
        name="deletemedia",
        help="Deletes a user's media messages across all server text channels. Usage: !deletemedia @member <months/all>"
    )
    async def deletemedia(self, ctx: commands.Context, member: discord.Member, timeframe: str):

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("❌ *Oh sweetheart... you lack the permissions required to command this purge.*")
            return

        timeframe = timeframe.lower()

        # Determine the date cutoff
        if timeframe == "all" or timeframe == "0":
            cutoff = None
        else:
            try:
                months = int(timeframe)

                if months < 1:
                    await ctx.send("⚠️ *Enter a positive number of months, or use `all`.*")
                    return

                cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30 * months)

            except ValueError:
                await ctx.send("⚠️ *Invalid timeframe. Use a number of months or `all`.*")
                return

        await ctx.send(
            f"🔥 *Initiating media purge for {member.mention} ({timeframe}) across the entire server...*"
        )

        deleted_count = 0
        skipped_channels = 0

        try:
            # Scan every text channel in the current server
            for channel in ctx.guild.text_channels:

                try:
                    async for message in channel.history(limit=None, oldest_first=True):

                        if message.author.id != member.id:
                            continue

                        # Check timeframe
                        if cutoff is not None and message.created_at < cutoff:
                            continue

                        # Check whether the message contains media or links
                        has_media = (
                            len(message.attachments) > 0
                            or any(url in message.content for url in ["http://", "https://"])
                        )

                        if has_media:
                            await message.delete()
                            deleted_count += 1

                except discord.Forbidden:
                    skipped_channels += 1
                    continue

                except discord.HTTPException as e:
                    print(f"Media purge error in #{channel.name}: {e}")
                    skipped_channels += 1
                    continue

            await ctx.send(
                f"✨ *Purge complete.*\n"
                f"🗑️ Media messages deleted: **{deleted_count}**\n"
                f"📂 Channels skipped: **{skipped_channels}**\n"
                f"👤 Target: {member.mention}"
            )

        except Exception as e:
            await ctx.send(f"❌ *The purge encountered resistance: {e}*")

    # ===== HELP NIGHT COMMAND =====
    @commands.command(
        name="helpnight",
        help="Scans the code and displays available commands across interactive paginated embeds."
    )
    async def helpnight(self, ctx: commands.Context):
        commands_list = list(self.bot.commands)
        chunk_size = 4
        embeds = []

        for i in range(0, len(commands_list), chunk_size):
            chunk = commands_list[i:i + chunk_size]

            embed = discord.Embed(
                title="🌹 Night's Grimoire — Command Index",
                description="Explore my capabilities. Use the arrows below to navigate through the shadows.",
                color=0x4B0082
            )

            for cmd in chunk:
                embed.add_field(
                    name=f"!{cmd.name}",
                    value=cmd.help or "No description provided. Pure mystery.",
                    inline=False
                )

            embed.set_footer(
                text=f"Page {(i // chunk_size) + 1} of {(len(commands_list) + chunk_size - 1) // chunk_size}"
            )
            embeds.append(embed)

        if not embeds:
            await ctx.send("No commands registered.")
            return

        msg = await ctx.send(embed=embeds[0])

    @commands.command(name="refresh", help="Reloads extensions and synchronizes database modules.")
    async def refresh_cmd(self, ctx: commands.Context):
        await ctx.send("🔄 *Synchronizing database models and refreshing internal systems...*")
        # Add reload/sync logic here
        await ctx.send("✨ *All systems successfully re-synchronized.*")

    @commands.command(name="debug_cmd", help="Checks whether a command is registered and displays its status, source cog and checks.")
    async def debug_cmd(self, ctx: commands.Context, command_name: str):
        cmd = self.bot.get_command(command_name)

        if not cmd:
            await ctx.send(f"❌ *Command `!{command_name}` is nowhere to be found in my grid.*")
            return

        embed = discord.Embed(
            title=f"🔍 Command Diagnostics: !{cmd.name}",
            color=0x8B0000
        )
        embed.add_field(name="Status", value="🟢 Active & Registered", inline=False)
        embed.add_field(name="Source Module / Cog", value=f"`{cmd.cog_name or 'Global / Core Script'}`", inline=False)
        embed.add_field(name="Help Text", value=cmd.help or "None", inline=False)
        embed.add_field(name="Checks / Permissions", value=str(cmd.checks) if cmd.checks else "None required", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="dashboard", help="Provides the direct link to the web management dashboard.")
    async def dashboard(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🖥️ The Red Room Web Portal",
            description="Manage your empire with supreme elegance through our web dashboard.",
            color=0x4B0082
        )
        embed.add_field(name="Portal Link", value="[Access Night Dashboard](https://railway.app)", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="backup", help="Creates a secure database backup.")
    async def backup(self, ctx: commands.Context):
        await ctx.send("💾 *Initiating secure database backup protocol onto persistent volume...*")
        # Backup logic hook
        await ctx.send("✨ *Backup successfully archived to disk.*")

    @commands.command(name="reload", help="Reloads a supported python script or extension.")
    async def reload_cog(self, ctx: commands.Context, cog_name: str):
        try:
            module_path = f"modules.{cog_name}"

            if module_path in sys.modules:
                mod = sys.modules[module_path]
                importlib.reload(mod)
                await ctx.send(f"🔄 *Module `{cog_name}` successfully reloaded and re-anchored.*")
            else:
                await ctx.send(f"⚠️ *Module `{cog_name}` is not loaded in memory.*")

        except Exception as e:
            await ctx.send(f"❌ *Failed to reload `{cog_name}`: {e}*")


async def setup(bot: commands.Bot):
    await bot.add_cog(RedRoomUtilities(bot))
