import discord
from discord.ext import commands
import datetime
from sqlalchemy.future import select
from core.database import AsyncSessionLocal
from database.global_models import GlobalUser, GlobalInventory

class EconomyModule(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_or_create_user(self, session, user_id: int) -> GlobalUser:
        result = await session.execute(select(GlobalUser).where(GlobalUser.user_id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = GlobalUser(user_id=user_id, lunas=100) # 100 Lunas welcome gift
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

    @commands.command(name="balance", aliases=["bal", "wallet", "lunas"], help="Checks your global Luna balance across all realms.")
    async def balance(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        
        async with AsyncSessionLocal() as session:
            user = await self.get_or_create_user(session, target.id)
            
            embed = discord.Embed(
                title=f"🌙 Vault of {target.display_name}",
                description=f"Your global wealth across the Night empire:\n\n💎 **{user.lunas:,} Lunas**",
                color=0x4B0082  # Luxurious Purple
            )
            embed.set_thumbnail(url=target.display_avatar.url)
            embed.set_footer(text="Earned worldwide. Spent wherever you desire.")
            await ctx.send(embed=embed)

    @commands.command(name="daily", help="Claims your daily tribute of Lunas to fuel your desires.")
    async def daily(self, ctx: commands.Context):
        now = datetime.datetime.utcnow()
        
        async with AsyncSessionLocal() as session:
            user = await self.get_or_create_user(session, ctx.author.id)
            
            if user.last_daily:
                elapsed = now - user.last_daily
                if elapsed.total_seconds() < 86400:
                    remaining = int(86400 - elapsed.total_seconds())
                    hours = remaining // 3600
                    minutes = (remaining % 3600) // 60
                    await ctx.send(f"⏳ *Patience, my sweet. Your next daily tribute of Lunas is ready in **{hours}h {minutes}m**.*")
                    return

            user.lunas += 250  # Daily payout
            user.last_daily = now
            await session.commit()

            embed = discord.Embed(
                title="🌹 Daily Tribute Collected",
                description=f"You claimed your daily **250 Lunas**.\nYour global vault now holds **{user.lunas:,} Lunas**.",
                color=0x8B0000  # Blood Red
            )
            await ctx.send(embed=embed)

    @commands.command(name="pay", aliases=[payments := "transfer"], help="Transfers Lunas from your global wallet to another member.")
    async def pay(self, ctx: commands.Context, member: discord.Member, amount: int):
        if member.id == ctx.author.id:
            await ctx.send("❌ *Trying to pay yourself? Clever, but the vault doesn't work that way.*")
            return
        
        if amount <= 0:
            await ctx.send("⚠️ *You must transfer a positive amount of Lunas.*")
            return

        async with AsyncSessionLocal() as session:
            sender = await self.get_or_create_user(session, ctx.author.id)
            
            if sender.lunas < amount:
                await ctx.send(f"❌ *Your global vault is too light. You only have **{sender.lunas:,} Lunas**.*")
                return

            receiver = await self.get_or_create_user(session, member.id)

            sender.lunas -= amount
            receiver.lunas += amount
            await session.commit()

            embed = discord.Embed(
                title="💸 Transfer Complete",
                description=f"You successfully transferred **{amount:,} Lunas** to {member.mention}.\nA transaction recorded across all shadows.",
                color=0x4B0082
            )
            await ctx.send(embed=embed)

    @commands.command(name="shop", help="Displays the global Red Room shop for purchasing items.")
    async def shop(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🛍️ The Red Room Global Boutique",
            description="Spend your hard-earned **Lunas**. Items purchased here stay on your global account forever.",
            color=0x8B0000
        )
        embed.add_field(
            name="1. Velvet Blindfold 🖤",
            value="Price: `500 Lunas`\n*Grants an exclusive cosmetic title in your global profile.*\nCommand: `!buy blindfold`",
            inline=False
        )
        embed.add_field(
            name="2. Master's Whip ⚡",
            value="Price: `1,200 Lunas`\n*Unlocks custom interactive power and special interaction flexes.*\nCommand: `!buy whip`",
            inline=False
        )
        embed.set_footer(text="Use !buy <item_name> to acquire your desires.")
        await ctx.send(embed=embed)

    @commands.command(name="buy", help="Purchases an item from the global shop.")
    async def buy(self, ctx: commands.Context, item_name: str):
        shop_items = {
            "blindfold": {"name": "Velvet Blindfold", "cost": 500},
            "whip": {"name": "Master's Whip", "cost": 1200}
        }

        key = item_name.lower()
        if key not in shop_items:
            await ctx.send("⚠️ *That item does not exist in our boutique. Check `!shop` for available treasures.*")
            return

        item_data = shop_items[key]

        async with AsyncSessionLocal() as session:
            user = await self.get_or_create_user(session, ctx.author.id)

            # Check if already owned
            existing = await session.execute(
                select(GlobalInventory).where(
                    GlobalInventory.user_id == ctx.author.id,
                    GlobalInventory.item_name == item_data["name"]
                )
            )
            if existing.scalar_one_or_none():
                await ctx.send(f"👑 *You already own the **{item_data['name']}** in your global inventory!*")
                return

            if user.lunas < item_data["cost"]:
                await ctx.send(f"❌ *Insufficient funds. You need **{item_data['cost']:,} Lunas**, but your vault only holds **{user.lunas:,} Lunas**.*")
                return

            # Deduct cost and add to inventory
            user.lunas -= item_data["cost"]
            new_item = GlobalInventory(user_id=ctx.author.id, item_name=item_data["name"])
            session.add(new_item)
            await session.commit()

            embed = discord.Embed(
                title="✨ Acquisition Successful",
                description=f"You purchased the **{item_data['name']}** for **{item_data['cost']:,} Lunas**.\nIt is now permanently bound to your global account.",
                color=0x4B0082
            )
            await ctx.send(embed=embed)

    @commands.command(name="inventory", aliases=["inv"], help="Inspects items stored in your global profile inventory.")
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author

        async with AsyncSessionLocal() as session:
            # Ensure user exists
            await self.get_or_create_user(session, target.id)

            result = await session.execute(
                select(GlobalInventory).where(GlobalInventory.user_id == target.id)
            )
            items = result.scalars().all()

            embed = discord.Embed(
                title=f"🎒 Global Inventory — {target.display_name}",
                description="Treasures and artifacts collected across all realms:",
                color=0x8B0000
            )

            if not items:
                embed.add_field(name="Empty Vault", value="*No items acquired yet. Visit `!shop` to browse.*", inline=False)
            else:
                item_list = "\n".join([f"• `{item.item_name}` (Acquired: {item.acquired_at.strftime('%Y-%m-%d')})" for item in items])
                embed.add_field(name="Owned Artifacts", value=item_list, inline=False)

            embed.set_thumbnail(url=target.display_avatar.url)
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyModule(bot))
