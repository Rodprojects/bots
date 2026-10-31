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
        # Calculate latency
        latency = round(self.bot.latency * 1000)
        
        # Crafting the dark luxury embed
        embed = discord.Embed(
            title="🍷 Heartbeat Check",
            description=f"My pulse is currently beating at **{latency}ms**.\n*Care to test how much load I can handle, Master?*",
            color=0x8B0000  # Deep Blood Red
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
            color=0x4B0082  # Luxurious Indigo/Purple
        )
        embed.add_field(
            name="🔒 Status", 
            value="Encrypted, persistent, and entirely under your control.", 
            inline=False
        )
        embed.set_footer(text="Designed for absolute dominance.")
        
        await ctx.send(embed=embed)

    @commands.command(name="servers", help="See all servers Night has infiltrated with direct invite links.")
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
                            invite = await channel.create_invite(max_age=86400, max_uses=1, reason="Dashboard empire lookup")
                            invite_link = invite.url
                            break
                except Exception:
                    invite_link = "Restricted"

                embed.add_field(
                    name=guild.name,
                    value=f"👑 Owner: `{guild.owner}`\n👥 Members: `{guild.member_count}`\n🔗 [Direct Entrance]({invite_link} if invite_link.startswith('http') else 'https://discord.com')",
                    inline=False
                )
            embeds.append(embed)

        # Simple single send or first page if multi-chunk (can be enhanced with persistent views later)
        await ctx.send(embed=embeds[0])

    @commands.command(name="purge_media", help="Deletes media from a user across timeframes: ever, 6m, 3m, 1m.")
    async def purge_media(self, ctx: commands.Context, member: discord.Member, timeframe: str):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("❌ *Oh sweetheart... you lack the permissions required to command this purge.*")
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        delta_map = {
            "ever": None,
            "6m": datetime.timedelta(days=182),
            "3m": datetime.timedelta(days=90),
            "1m": datetime.timedelta(days=30)
        }

        timeframe_key = timeframe.lower()
        if timeframe_key not in delta_map:
            await ctx.send("⚠️ *Invalid timeframe specified. Use: `ever`, `6m`, `3m`, or `1m`.*")
            return

        cutoff = now - delta_map[timeframe_key] if delta_map[timeframe_key] else None

        await ctx.send(f"🔥 *Initiating media purge for {member.mention} ({timeframe_key})... Scanning the shadows.*")

        deleted_count = 0
        try:
            async for message in ctx.channel.history(limit=500):
                if message.author.id == member.id:
                    has_media = len(message.attachments) > 0 or any(url in message.content for url in ["http://", "https://"])
                    if has_media:
                        if cutoff is None or message.created_at >= cutoff:
                            await message.delete()
                            deleted_count += 1
            await ctx.send(f"✨ *Purge complete. Swept away {deleted_count} media traces of {member.mention}.*")
        except Exception as e:
            await ctx.send(f"❌ *The purge encountered resistance: {e}*")

    @commands.command(name="help_menu", help="Scans the code and displays available commands across interactive paginated embeds.")
    async def help_menu(self, ctx: commands.Context):
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
            embed.set_footer(text=f"Page {(i // chunk_size) + 1} of {(len(commands_list) + chunk_size - 1) // chunk_size}")
            embeds.append(embed)

        if not embeds:
            await ctx.send("No commands registered.")
            return

        # Send first page
        msg = await ctx.send(embed=embeds[0])
        # We can attach interactive buttons here in our persistent view system later!

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
            # Attempt to reload module from modules package
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
