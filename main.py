import discord
from discord.ext import commands
import os

TOKEN = os.getenv("TOKEN")

ADMIN_DASHBOARD_ID = 1501167503185805403
LOG_CHANNEL_ID = 1496076202509598720
CUSTOMER_ROLE_ID = 1488092810442706994

# ===== intents =====
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== PRODUCTS =====
PRODUCTS = {
    "v1": {
        "name": "SETTING V1",
        "price": "79 THB",
        "emoji": "🔥",
        "item": "ลิงก์ดาวน์โหลด V1: https://example.com/v1"
    },
    "v2": {
        "name": "KINGWEAPON V2",
        "price": "99 THB",
        "emoji": "👑",
        "item": "ลิงก์ดาวน์โหลด V2: https://example.com/v2"
    },
    "pro": {
        "name": "FPS BOOSTER PRO",
        "price": "45 THB",
        "emoji": "⚡",
        "item": "ไฟล์โปร: https://example.com/pro"
    }
}

# ===== PAYMENT =====
PAYMENT_INFO = {
    "bank_name": "กรุงไทย",
    "bank_number": "665-2-19754-5",
    "wallet_number": "065-529-2340",
    "account_name": "ปุณณวิช"
}


# ===== PAYMENT VIEW =====
class PaymentView(discord.ui.View):
    def __init__(self, product_id):
        super().__init__(timeout=None)
        self.data = PRODUCTS.get(product_id)

    @discord.ui.button(
        label="ดูช่องทางชำระเงิน",
        style=discord.ButtonStyle.secondary,
        custom_id="pay_info"
    )
    async def payinfo(self, interaction: discord.Interaction, button: discord.ui.Button):
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

    @discord.ui.button(
        label="แจ้งโอนแล้ว",
        style=discord.ButtonStyle.success,
        custom_id="confirm_pay"
    )
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 🔥 กันกดซ้ำ
        button.disabled = True
        await interaction.message.edit(view=self)

        # ===== LOG =====
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"💸 {interaction.user.mention} แจ้งโอน {self.data['name']}"
            )

        # ===== ให้ ROLE =====
        role = interaction.guild.get_role(CUSTOMER_ROLE_ID)
        if role:
            await interaction.user.add_roles(role)

        # ===== ส่งของ (DM) =====
        try:
            await interaction.user.send(
                f"🎁 สินค้าของคุณ:\n{self.data['item']}"
            )
        except:
            pass

        await interaction.response.send_message("สำเร็จแล้ว ✅", ephemeral=True)


# ===== STOREFRONT =====
class StorefrontView(discord.ui.View):
    def __init__(self, product_id):
        super().__init__(timeout=None)
        self.product_id = product_id

    @discord.ui.button(
        label="ซื้อ",
        style=discord.ButtonStyle.success,
        custom_id="buy_btn"
    )
    async def buy(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            view=PaymentView(self.product_id),
            ephemeral=True
        )


# ===== MODAL =====
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
            await interaction.response.send_message("ส่งสินค้าแล้ว ✅", ephemeral=True)

        except:
            await interaction.response.send_message("ID ผิด ❌", ephemeral=True)


# ===== ADMIN =====
class AdminControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        for p_id in PRODUCTS:
            self.add_item(discord.ui.Button(
                label=PRODUCTS[p_id]['name'],
                style=discord.ButtonStyle.primary,
                custom_id=f"admin_{p_id}"
            ))

    async def interaction_check(self, interaction: discord.Interaction):
        custom_id = interaction.data.get("custom_id")

        if custom_id.startswith("admin_"):
            p_id = custom_id.replace("admin_", "")
            await interaction.response.send_modal(ChannelIDModal(p_id))
            return False

        return True


# ===== BOT =====
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_view(AdminControlView())


bot = Bot()


# ===== COMMAND =====
@bot.command()
async def dashboard(ctx):
    if ctx.channel.id != ADMIN_DASHBOARD_ID:
        return
    await ctx.send("CONTROL PANEL", view=AdminControlView())


# ===== READY =====
@bot.event
async def on_ready():
    print("ONLINE")


bot.run(TOKEN)
