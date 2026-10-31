import discord
from discord.ext import commands
import datetime
import random
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.global_models import GlobalUser

class PlayfulActions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Dictionary tracking separate 12-hour cooldowns per user and per command action
        self.action_cooldowns = {}

    async def _process_action(self, ctx: commands.Context, action_name: str, target: discord.Member = None, secondary_target: discord.Member = None):
        now = datetime.datetime.utcnow()
        user_key = (ctx.author.id, action_name)

        # Per-action 12-hour cooldown check
        if user_key in self.action_cooldowns:
            last_used = self.action_cooldowns[user_key]
            elapsed = (now - last_used).total_seconds()
            if elapsed < 43200:  # 12 hours
                remaining = int(43200 - elapsed)
                hours = remaining // 3600
                minutes = (remaining % 3600) // 60
                await ctx.send(f"⏳ *Patience... You must wait **{hours}h {minutes}m** before using **!{action_name}** again.*")
                return

        async with AsyncSessionLocal() as session:
            # Fetch or create author profile
            res_author = await session.execute(select(GlobalUser).where(GlobalUser.user_id == ctx.author.id))
            author_db = res_author.scalar_one_or_none()
            if not author_db:
                author_db = GlobalUser(user_id=ctx.author.id, lunas=100, actions_given=0, actions_received=0)
                session.add(author_db)

            if author_db.lunas is None:
                author_db.lunas = 100
            if author_db.actions_given is None:
                author_db.actions_given = 0

            # Determine reward & apply updates
            lunas_earned = random.randint(20, 100)
            author_db.lunas += lunas_earned
            author_db.last_action = now
            author_db.actions_given += 1

            # Update target statistics if target exists
            if target and target.id != ctx.author.id:
                res_target = await session.execute(select(GlobalUser).where(GlobalUser.user_id == target.id))
                target_db = res_target.scalar_one_or_none()
                if not target_db:
                    target_db = GlobalUser(user_id=target.id, lunas=100, actions_given=0, actions_received=0)
                    session.add(target_db)
                if target_db.actions_received is None:
                    target_db.actions_received = 0
                target_db.actions_received += 1

            if secondary_target and secondary_target.id != ctx.author.id:
                res_target2 = await session.execute(select(GlobalUser).where(GlobalUser.user_id == secondary_target.id))
                target2_db = res_target2.scalar_one_or_none()
                if not target2_db:
                    target2_db = GlobalUser(user_id=secondary_target.id, lunas=100, actions_given=0, actions_received=0)
                    session.add(target2_db)
                if target2_db.actions_received is None:
                    target2_db.actions_received = 0
                target2_db.actions_received += 1

            await session.commit()

        # Update individual action cooldown stamp
        self.action_cooldowns[user_key] = now

        # Format public response based on targeting
        if action_name == "threesome":
            t1 = target.mention if target else ctx.author.mention
            t2 = secondary_target.mention if secondary_target else "the shadow"
            desc = f"{ctx.author.mention} initiates a playful encounter with {t1} and {t2}!"
        else:
            t_str = target.mention if target else ctx.author.mention
            desc = f"{ctx.author.mention} executes **!{action_name}** on {t_str}!"

        embed = discord.Embed(
            title=f"🔥 Action: {action_name.capitalize()}",
            description=f"{desc}\n\n✨ Earned **+{lunas_earned} Lunas**.",
            color=0x8B0000
        )
        embed.set_footer(text=f"Cooldown for !{action_name}: 12 Hours")
        await ctx.send(embed=embed)

    @commands.command(name="whip")
    async def whip(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "whip", member)

    @commands.command(name="tie")
    async def tie(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "tie", member)

    @commands.command(name="spank")
    async def spank(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "spank", member)

    @commands.command(name="beg")
    async def beg(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "beg", member)

    @commands.command(name="gag")
    async def gag(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "gag", member)

    @commands.command(name="spit")
    async def spit(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "spit", member)

    @commands.command(name="slut")
    async def slut(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "slut", member)

    @commands.command(name="pimp")
    async def pimp(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "pimp", member)

    @commands.command(name="choke")
    async def choke(self, ctx, member: discord.Member = None):
        await self._process_action(ctx, "choke", member)

    @commands.command(name="threesome")
    async def threesome(self, ctx, member1: discord.Member = None, member2: discord.Member = None):
        await self._process_action(ctx, "threesome", member1, member2)

async def setup(bot: commands.Bot):
    await bot.add_cog(PlayfulActions(bot))
