import discord
from discord.ext import commands
import os
from datetime import datetime

TOKEN = os.getenv("TOKEN")

ADMIN_DASHBOARD_ID = 1501167503185805403
LOG_CHANNEL_ID = 1496076202509598720
CUSTOM_ROLE_ID = 1488092810442706994

PRODUCTS = {
    "v1": {
        "name": "SETTING V1",
        "price": "79 THB",
        "emoji": "🔥",
        "item": "ลิงก์โหลด V1"
    },
    "v2": {
        "name": "KINGWEAPON V2",
        "price": "99 THB",
        "emoji": "👑",
        "item": "ลิงก์โหลด V2"
    },
    "pro": {
        "name": "FPS BOOSTER PRO",
        "price": "45 THB",
        "emoji": "⚡",
        "item": "ลิงก์โหลด PRO"
    }
}

PAYMENT_INFO = {
    "bank_name": "กรุงไทย",
    "bank_number": "665-2-19754-5",
    "wallet_number": "065-529-2340",
    "account_name": "ปุณณวิช"
}

# ===========================
# 💳 PAYMENT VIEW
# ===========================
class PaymentView(discord.ui.View):
    def __init__(self, product_id):
        super().__init__(timeout=None)
        self.product_id = product_id
        self.data = PRODUCTS[product_id]

    @discord.ui.button(
        label="💳 ช่องทางชำระเงิน",
        style=discord.ButtonStyle.secondary,
        custom_id="payinfo_global"
    )
    async def payinfo(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="📱 วิธีชำระเงิน", color=0x00ffff)
        embed.description = (
            f"**{self.data['name']}**\nราคา: {self.data['price']}\n\n"
            f"🏦 {PAYMENT_INFO['bank_name']} : {PAYMENT_INFO['bank_number']}\n"
            f"📱 Wallet : {PAYMENT_INFO['wallet_number']}"
        )

        qr_path = "qrcode.png"

        if os.path.exists(qr_path):
            file = discord.File(qr_path, filename="qr.png")
            embed.set_image(url="attachment://qr.png")
            await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="✅ แจ้งโอนแล้ว",
        style=discord.ButtonStyle.success,
        custom_id="confirm_global"
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        # ===== LOG =====
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="💸 แจ้งโอนเงิน",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="👤 ผู้ใช้", value=interaction.user.mention, inline=False)
            embed.add_field(name="📦 สินค้า", value=self.data['name'], inline=False)
            embed.add_field(name="💰 ราคา", value=self.data['price'], inline=False)

            await log_channel.send(embed=embed)

        # ===== GIVE ROLE =====
        role = interaction.guild.get_role(CUSTOM_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)

        # ===== SEND ITEM =====
        try:
            await interaction.user.send(f"🎁 สินค้า:\n{self.data['item']}")
        except:
            await interaction.channel.send(f"{interaction.user.mention} เปิด DM ไม่ได้")

        await interaction.followup.send("✅ แจ้งโอนเรียบร้อย!", ephemeral=True)


# ===========================
# 🛒 STORE
# ===========================
class StorefrontView(discord.ui.View):
    def __init__(self, product_id):
        super().__init__(timeout=None)
        self.product_id = product_id

        btn = discord.ui.Button(
            label="🛒 ซื้อสินค้า",
            style=discord.ButtonStyle.success,
            custom_id=f"buy_{product_id}"
        )
        btn.callback = self.buy
        self.add_item(btn)

    async def buy(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "💳 เลือกวิธีชำระเงิน",
            view=PaymentView(self.product_id),
            ephemeral=True
        )


# ===========================
# 🧠 MODAL
# ===========================
class ChannelIDModal(discord.ui.Modal, title="📌 ส่งสินค้า"):
    channel_id_input = discord.ui.TextInput(label="Channel ID")

    def __init__(self, product_id):
        super().__init__()
        self.product_id = product_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel = interaction.guild.get_channel(int(self.channel_id_input.value))
            data = PRODUCTS[self.product_id]

            embed = discord.Embed(
                title=f"{data['emoji']} {data['name']}",
                description=f"💰 ราคา: {data['price']}",
                color=0x5865F2
            )

            await channel.send(embed=embed, view=StorefrontView(self.product_id))
            await interaction.response.send_message("✅ ส่งแล้ว", ephemeral=True)

        except:
            await interaction.response.send_message("❌ ID ผิด", ephemeral=True)


# ===========================
# 🎛 CONTROL PANEL
# ===========================
class AdminControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        for p_id in PRODUCTS:
            btn = discord.ui.Button(
                label=PRODUCTS[p_id]['name'],
                emoji=PRODUCTS[p_id]['emoji'],
                style=discord.ButtonStyle.primary,
                custom_id=f"admin_{p_id}"   # 🔥 FIX
            )
            btn.callback = self.make_callback(p_id)
            self.add_item(btn)

    def make_callback(self, p_id):
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_modal(ChannelIDModal(p_id))
        return callback


# ===========================
# 🤖 BOT
# ===========================
class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 🔥 IMPORTANT: persistent views
        self.add_view(AdminControlView())
        self.add_view(StorefrontView("v1"))
        self.add_view(StorefrontView("v2"))
        self.add_view(StorefrontView("pro"))
        self.add_view(PaymentView("v1"))
        self.add_view(PaymentView("v2"))
        self.add_view(PaymentView("pro"))


bot = Bot()


# ===========================
# 📊 COMMAND
# ===========================
@bot.command()
async def dashboard(ctx):
    if ctx.channel.id != ADMIN_DASHBOARD_ID:
        return

    embed = discord.Embed(
        title="🎛 CONTROL PANEL",
        description="เลือกระบบสินค้า",
        color=0x2f3136
    )

    await ctx.send(embed=embed, view=AdminControlView())


@bot.event
async def on_ready():
    print(f"ONLINE: {bot.user}")


bot.run(TOKEN)
