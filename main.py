import discord
from discord.ext import commands
import os



TOKEN = os.getenv("TOKEN")
ADMIN_DASHBOARD_ID = 1501167503185805403 

PRODUCTS = {
    "v1": {"name": "SETTING V1", "price": "79 THB", "emoji": "🔥"},
    "v2": {"name": "KINGWEAPON V2", "price": "99 THB", "emoji": "👑"},
    "pro": {"name": "FPS BOOSTER PRO", "price": "45 THB", "emoji": "⚡"}
}

PAYMENT_INFO = {
    "bank_name": "กรุงไทย",
    "bank_number": "665-2-19754-5",
    "wallet_number": "0xx-xxx-xxxx",
    "account_name": "ปุณณวิช"
}

class PaymentView(discord.ui.View):
    def __init__(self, product_id):
        super().__init__(timeout=None)
        self.data = PRODUCTS.get(product_id)

@discord.ui.button(label="ดูช่องทางชำระเงิน", style=discord.ButtonStyle.secondary)
async def qrcode(self, interaction: discord.Interaction, button: discord.ui.Button):
    embed = discord.Embed(title="📱 ชำระเงิน", color=0x00ffff)
    embed.description = (
        f"{self.data['name']} - {self.data['price']}\n\n"
        f"{PAYMENT_INFO['bank_name']} : {PAYMENT_INFO['bank_number']}\n"
        f"Wallet : {PAYMENT_INFO['wallet_number']}"
    )

    qr_path = "qrcode.png"

    if os.path.exists(qr_path):
        file = discord.File(qr_path, filename="qr.png")
        embed.set_image(url="attachment://qr.png")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="แจ้งโอนแล้ว", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.send(f"🔔 {interaction.user.mention} แจ้งโอน {self.data['name']}")
        await interaction.response.send_message("ส่งแล้ว", ephemeral=True)

class StorefrontView(discord.ui.View):
    def __init__(self, product_id):
        super().__init__(timeout=None)
        btn = discord.ui.Button(label="ซื้อ", style=discord.ButtonStyle.success)
        btn.callback = self.buy
        self.product_id = product_id
        self.add_item(btn)

    async def buy(self, interaction: discord.Interaction):
        await interaction.response.send_message(view=PaymentView(self.product_id), ephemeral=True)

class ChannelIDModal(discord.ui.Modal, title='ใส่ ID ห้อง'):
    channel_id_input = discord.ui.TextInput(label='Channel ID')

    def __init__(self, product_id):
        super().__init__()
        self.product_id = product_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel = interaction.guild.get_channel(int(self.channel_id_input.value))
            data = PRODUCTS[self.product_id]

            embed = discord.Embed(
                title=f"{data['emoji']} {data['name']}",
                description=f"{data['price']}",
                color=0x5865F2
            )

            await channel.send(embed=embed, view=StorefrontView(self.product_id))
            await interaction.response.send_message("ส่งแล้ว", ephemeral=True)
        except:
            await interaction.response.send_message("ผิด", ephemeral=True)

class AdminControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for p_id in PRODUCTS:
            btn = discord.ui.Button(label=PRODUCTS[p_id]['name'])
            btn.callback = self.make_callback(p_id)
            self.add_item(btn)

    def make_callback(self, p_id):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_modal(ChannelIDModal(p_id))
        return callback

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.add_view(AdminControlView())

bot = Bot()

@bot.command()
async def dashboard(ctx):
    if ctx.channel.id != ADMIN_DASHBOARD_ID:
        return
    await ctx.send("CONTROL", view=AdminControlView())

@bot.event
async def on_ready():
    print("ONLINE")

bot.run(TOKEN)