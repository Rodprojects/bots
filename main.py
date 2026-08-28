import sqlite3
import discord
from discord.ext import commands

# ---------------------------------------------------------------------------
# CONFIGURATION & GALACTIC BLUE THEME
# ---------------------------------------------------------------------------
TOKEN = "YOUR_BOT_TOKEN_HERE"
GALACTIC_BLUE = discord.Color.from_rgb(11, 29, 58)      # #0B1D3A
GALACTIC_ACCENT = discord.Color.from_rgb(0, 102, 204)    # #0066CC
NEBULA_DARK = discord.Color.from_rgb(5, 10, 25)         # #050A19

# Initialize SQLite database
conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS dm_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending'
)
""")
conn.commit()


# ---------------------------------------------------------------------------
# PERSISTENT VIEW (BUTTONS NEVER EXPIRE)
# ---------------------------------------------------------------------------
class DMRequestView(discord.ui.View):
    def __init__(self, sender_id: int, target_id: int):
        # Setting timeout=None ensures the view listens indefinitely without expiring
        super().__init__(timeout=None)
        self.sender_id = sender_id
        self.target_id = target_id

    @discord.ui.button(
        label="Accept Request", 
        style=discord.ButtonStyle.primary, 
        emoji="🌌", 
        custom_id="ask_dm_accept"
    )
    async def accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Verification check
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("✨ This request was not sent to you.", ephemeral=True)
            return

        # Update Database
        cursor.execute(
            "UPDATE dm_requests SET status = 'accepted' WHERE sender_id = ? AND target_id = ?",
            (self.sender_id, self.target_id)
        )
        conn.commit()

        # Visual feedback for accepted request
        embed = discord.Embed(
            title="🌌 Connection Established",
            description=f"You have accepted the DM invitation from <@{self.sender_id}>!\nFeel free to open your direct message channel with them.",
            color=GALACTIC_ACCENT
        )
        embed.set_footer(text="Galactic DM Engine • Safe & Encrypted Link")

        # Disable all buttons post-interaction
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)

        # Notify the sender via DM
        try:
            sender = await interaction.client.fetch_user(self.sender_id)
            notify_embed = discord.Embed(
                title="💫 Request Accepted",
                description=f"<@{self.target_id}> accepted your **Ask to DM** request!",
                color=GALACTIC_BLUE
            )
            await sender.send(embed=notify_embed)
        except discord.HTTPException:
            pass

    @discord.ui.button(
        label="Decline", 
        style=discord.ButtonStyle.danger, 
        emoji="🌠", 
        custom_id="ask_dm_decline"
    )
    async def decline_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_id:
            await interaction.response.send_message("✨ This request was not sent to you.", ephemeral=True)
            return

        # Update Database
        cursor.execute(
            "UPDATE dm_requests SET status = 'declined' WHERE sender_id = ? AND target_id = ?",
            (self.sender_id, self.target_id)
        )
        conn.commit()

        embed = discord.Embed(
            title="🪐 Connection Closed",
            description="You declined the DM request.",
            color=NEBULA_DARK
        )
        
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(embed=embed, view=self)


# ---------------------------------------------------------------------------
# BOT ENGINE INITIALIZATION
# ---------------------------------------------------------------------------
class GalacticBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Register persistent views globally on startup so old buttons remain active
        cursor.execute("SELECT sender_id, target_id FROM dm_requests WHERE status = 'pending'")
        requests = cursor.fetchall()
        for sender_id, target_id in requests:
            self.add_view(DMRequestView(sender_id, target_id))


bot = GalacticBot()


# ---------------------------------------------------------------------------
# COMMANDS & VISUAL ENGINE
# ---------------------------------------------------------------------------
@bot.command(name="ask")
async def ask_dm(ctx: commands.Context, member: discord.Member = None):
    """Command to ask a member for permission to DM."""
    if member is None or member.bot or member == ctx.author:
        embed_err = discord.Embed(
            title="🌌 Cosmic Alignment Error",
            description="Please specify a valid member to request: `!ask @member`",
            color=GALACTIC_BLUE
        )
        await ctx.send(embed=embed_err)
        return

    # Check if a pending request already exists in SQLite
    cursor.execute(
        "SELECT id FROM dm_requests WHERE sender_id = ? AND target_id = ? AND status = 'pending'",
        (ctx.author.id, member.id)
    )
    if cursor.fetchone():
        embed_exist = discord.Embed(
            title="💫 Signal Pending",
            description=f"You already have an active pending request to {member.mention}.",
            color=GALACTIC_ACCENT
        )
        await ctx.send(embed=embed_exist)
        return

    # Save request into .db file
    cursor.execute(
        "INSERT INTO dm_requests (sender_id, target_id, status) VALUES (?, ?, 'pending')",
        (ctx.author.id, member.id)
    )
    conn.commit()

    # Build Galactic Visual Embed for DM
    dm_embed = discord.Embed(
        title="🪐 Incoming Galactic Signal",
        description=(
            f"Greetings **{member.display_name}**,\n\n"
            f"User **{ctx.author.name}** (`{ctx.author.id}`) is requesting permission "
            f"to initiate a private transmission in DM."
        ),
        color=GALACTIC_BLUE
    )
    dm_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    dm_embed.add_field(name="Server Origin", value=f"• {ctx.guild.name}", inline=True)
    dm_embed.add_field(name="Theme", value="• Cosmic NSFW", inline=True)
    dm_embed.set_footer(text="Click a button below to accept or decline • Buttons never expire")

    # Send DM with the persistent view engine
    try:
        view = DMRequestView(sender_id=ctx.author.id, target_id=member.id)
        await member.send(embed=dm_embed, view=view)

        # Confirm in server channel
        confirm_embed = discord.Embed(
            title="✨ Signal Transmitted",
            description=f"Your DM request has been sent to {member.mention}.",
            color=GALACTIC_ACCENT
        )
        await ctx.send(embed=confirm_embed)

    except discord.Forbidden:
        embed_fail = discord.Embed(
            title="☄️ Transmission Blocked",
            description=f"Could not reach {member.mention}. Their DMs might be locked or closed.",
            color=NEBULA_DARK
        )
        await ctx.send(embed=embed_fail)


@bot.event
async def on_ready():
    print(f"[{bot.user.name}] Galactic Engine Online & Listening...")


if __name__ == "__main__":
    bot.run(TOKEN)
