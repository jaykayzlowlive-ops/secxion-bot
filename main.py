import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ===== VIEW =====
class AdminControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="กดปุ่มนี้",
        style=discord.ButtonStyle.primary,
        custom_id="admin_btn_1"
    )
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("คุณกดปุ่มแล้ว!", ephemeral=True)

    @discord.ui.button(
        label="ปุ่มลบ",
        style=discord.ButtonStyle.danger,
        custom_id="admin_btn_2"
    )
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("กดปุ่มลบแล้ว!", ephemeral=True)


# ===== SETUP =====
@bot.event
async def setup_hook():
    bot.add_view(AdminControlView())


# ===== COMMAND =====
@bot.command()
async def panel(ctx):
    await ctx.send("แผงควบคุม:", view=AdminControlView())


# ===== READY =====
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ===== RUN =====
bot.run(TOKEN)
