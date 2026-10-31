import discord
from discord.ext import commands
import sys
import os
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.global_models import GlobalUser, GlobalInventory
from database.guild_models import GuildConfig
from utils.decorators import has_night_admin_permission

class AdminDiagnostics(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="runcheck", help="Performs a deep diagnostic scan of code modules, database tables, and command conflicts.")
    @has_night_admin_permission()
    async def runcheck(self, ctx: commands.Context):
        await ctx.send("🔍 *Initiating deep system scan across Night's infrastructure... Please wait.*")

        report_lines = []
        has_errors = False

        # 1. Check Bot Intents
        intents = self.bot.intents
        intents_status = []
        if intents.message_content:
            intents_status.append("🟢 Message Content")
        else:
            intents_status.append("🔴 Message Content (DISABLED - Commands will fail!)")
            has_errors = True

        if intents.members:
            intents_status.append("🟢 Server Members")
        else:
            intents_status.append("🟡 Server Members (Disabled)")

        report_lines.append(f"**Gateway Intents:**\n" + "\n".join([f"• {s}" for s in intents_status]))

        # 2. Check Loaded Modules / Cogs
        loaded_cogs = list(self.bot.cogs.keys())
        report_lines.append(f"\n**Loaded Modules ({len(loaded_cogs)} active):**\n" + "".join([f"• `{cog}`\n" for cog in loaded_cogs]))

        # 3. Check Command Conflicts / Duplicates
        command_names = {}
        duplicates = []
        for cmd in self.bot.commands:
            # Check primary name
            if cmd.name in command_names:
                duplicates.append(cmd.name)
            else:
                command_names[cmd.name] = cmd.cog_name
            # Check aliases
            for alias in cmd.aliases:
                if alias in command_names:
                    duplicates.append(alias)
                else:
                    command_names[alias] = cmd.cog_name

        if duplicates:
            has_errors = True
            report_lines.append(f"\n⚠️ **Command Conflicts Detected:**\n• Duplicate names/aliases found: `{', '.join(set(duplicates))}`")
        else:
            report_lines.append(f"\n**Command Registry:**\n• 🟢 Zero naming conflicts. All `{len(command_names)}` commands & aliases are unique.")

        # 4. Check Database Connectivity & Tables
        db_status = "🟢 Connected & Operational"
        db_error_msg = ""
        try:
            async with AsyncSessionLocal() as session:
                # Test query on global users
                await session.execute(select(GlobalUser).limit(1))
                # Test query on guild configs
                await session.execute(select(GuildConfig).limit(1))
        except Exception as e:
            has_errors = True
            db_status = "🔴 Database Error / Missing Tables"
            db_error_msg = f"\n*Error:* `{e}`"

        report_lines.append(f"\n**Database Volume Integrity:**\n• Status: {db_status}{db_error_msg}")

        # Final Embed Output
        embed_color = 0x8B0000 if has_errors else 0x4B0082
        embed_title = "⚠️ Diagnostic Scan: Issues Found" if has_errors else "✨ Diagnostic Scan: All Systems Pristine"

        embed = discord.Embed(
            title=embed_title,
            description="\n".join(report_lines),
            color=embed_color
        )
        embed.set_footer(text="Night Ecosystem — Autonomous Diagnostics Protocol")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminDiagnostics(bot))
