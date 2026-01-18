import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1314991397585031281  # optional, speeds up slash commands
ACCESS_ROLE_ID = 1348245852874997822  # role granted on success
# REQUIRED TVA TIME (this is the key)
REQUIRED_HOUR = 6
REQUIRED_MINUTE = 0

# --- USER STATE ---
user_state = {}  # user_id: {"hour": None, "minute": None}

# --- TVA VIEW: START ---
class StartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Begin Calibration", style=discord.ButtonStyle.success)
    async def begin(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_state[interaction.user.id] = {"hour": None, "minute": None}

        embed = discord.Embed(
            title="⏰ TVA Calibration — Phase I",
            description=(
                "Variant detected.\n\n"
                "**Align the PRIMARY TIMELINE HOUR.**\n"
                "Incorrect inputs may cause a Nexus Event."
            ),
            color=0x2ECC71
        )

        await interaction.response.edit_message(embed=embed, view=HourView())

# --- HOUR SELECTION ---
class HourView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for hour in [1, 3, 5, 6, 7]:
            self.add_item(HourButton(hour))

class HourButton(discord.ui.Button):
    def __init__(self, hour: int):
        super().__init__(
            label=str(hour),
            style=discord.ButtonStyle.primary
        )
        self.hour = hour

    async def callback(self, interaction: discord.Interaction):
        user_state[interaction.user.id]["hour"] = self.hour

        if self.hour != REQUIRED_HOUR:
            embed = discord.Embed(
                title="⚠️ Timeline Divergence",
                description="Are you **sure** this is correct, Variant?",
                color=0xE74C3C
            )
            await interaction.response.edit_message(embed=embed, view=HourView())
            return

        embed = discord.Embed(
            title="⏳ TVA Calibration — Phase II",
            description="Primary hour stabilized.\n\n**Set the MINUTE MARKER.**",
            color=0x3498DB
        )

        await interaction.response.edit_message(embed=embed, view=MinuteView())

# --- MINUTE SELECTION ---
class MinuteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        for minute in [0, 15, 30, 45]:
            self.add_item(MinuteButton(minute))

class MinuteButton(discord.ui.Button):
    def __init__(self, minute: int):
        super().__init__(
            label=f"{minute:02d}",
            style=discord.ButtonStyle.secondary
        )
        self.minute = minute

    async def callback(self, interaction: discord.Interaction):
        user_state[interaction.user.id]["minute"] = self.minute

        if self.minute != REQUIRED_MINUTE:
            embed = discord.Embed(
                title="❌ Nexus Event Detected",
                description="Temporal instability rising. Recalibrate.",
                color=0xE67E22
            )
            await interaction.response.edit_message(embed=embed, view=MinuteView())
            return

        # SUCCESS
        role = interaction.guild.get_role(ACCESS_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)

        embed = discord.Embed(
            title="🌀 Timeline Secured",
            description=(
                "**Calibration Complete.**\n\n"
                f"🕰️ Time Entered: **{REQUIRED_HOUR}:{REQUIRED_MINUTE:02d}**\n"
                "Status: **APPROVED VARIANT**"
            ),
            color=0x9B59B6
        )

        await interaction.response.edit_message(embed=embed, view=None)

# --- SLASH COMMAND ---
@bot.tree.command(name="tva", description="Begin TVA timeline calibration")
async def tva(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🟢 Time Variance Authority",
        description=(
            "Variant detected.\n"
            "Temporal aura unstable.\n\n"
            "*Do you wish to proceed with calibration?*"
        ),
        color=0x1ABC9C
    )

    await interaction.response.send_message(embed=embed, view=StartView(), ephemeral=True)

# --- READY ---
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
