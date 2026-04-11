import discord
import logging
from discord import app_commands, Interaction, Embed, Color, SelectOption
from discord.ui import View, Select, Modal, TextInput
from setup import bot
import os
import requests
from database import save_user_mapping, get_user_config
from config import BOARDS, COLUMN_NAMES, TEAM_ID, BASE_URL, get_column_id

logger = logging.getLogger("GDSCommander.superthread")

# --- UI Components ---

class SetupWizard(View):
    def __init__(self, discord_id):
        super().__init__(timeout=180)
        self.discord_id = discord_id
        self.user_id = None

    @discord.ui.button(label="🔗 Link Superthread ID", style=discord.ButtonStyle.primary)
    async def link_id(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LinkIDModal(self))

class LinkIDModal(Modal, title="Link Superthread Account"):
    user_id = TextInput(
        label="Superthread User ID", 
        placeholder="Starts with 'u' (e.g. uRszeGJR...)",
        min_length=5,
        max_length=50
    )

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: Interaction):
        self.parent_view.user_id = self.user_id.value
        # Move to board selection
        view = BoardSelectView(self.parent_view)
        await interaction.response.send_message(
            f"✅ ID Recorded! Now, please select your **Primary Team/Board**:", 
            view=view, 
            ephemeral=True
        )

class BoardSelectView(View):
    def __init__(self, parent_view):
        super().__init__(timeout=120)
        self.parent_view = parent_view

    @discord.ui.select(
        placeholder="Choose your Team",
        options=[SelectOption(label=name, value=id) for name, id in BOARDS.items()]
    )
    async def select_board(self, interaction: Interaction, select: discord.ui.Select):
        board_id = select.values[0]
        board_name = [name for name, id in BOARDS.items() if id == board_id][0]
        
        # We store "Linked via ID" in the email column since we are deprecating email lookup
        save_user_mapping(
            self.parent_view.discord_id, 
            "Linked via ID", 
            self.parent_view.user_id, 
            board_id
        )
        
        await interaction.response.send_message(
            f"✅ **Setup Complete!**\n"
            f"Linked to `{board_name}` as User `{self.parent_view.user_id}`.\n\n"
            "You can now use `/st_create` to create cards directly!", 
            ephemeral=True
        )

# --- Card Creation ---

class CardModal(Modal, title="Create Superthread Card"):
    card_title = TextInput(label="Title", placeholder="What is the task?")
    card_desc = TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, board_name, board_id, column_name):
        super().__init__()
        self.board_name = board_name
        self.board_id = board_id
        self.column_name = column_name

    async def on_submit(self, interaction: Interaction):
        column_id = get_column_id(self.board_id, self.column_name)
        
        # Headers for API
        token = os.getenv("PERSONAL_API_TOKEN_SUPERTHREAD")
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        
        payload = {
            "title": self.card_title.value,
            "content": self.card_desc.value or "",
            "board_id": self.board_id,
            "list_id": column_id
        }
        
        url = f"{BASE_URL}/{TEAM_ID}/cards"
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            embed = Embed(title="✅ Card Created!", color=discord.Color.green())
            embed.add_field(name="Title", value=self.card_title.value, inline=False)
            embed.add_field(name="Destination", value=f"{self.board_name} > {self.column_name}", inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ Superthread API Error: {response.status_code}", ephemeral=True)

class CardCreationView(View):
    def __init__(self, user_config):
        super().__init__(timeout=120)
        self.board_id = user_config.get('board_id')
        self.board_name = [name for name, id in BOARDS.items() if id == self.board_id][0] if self.board_id else next(iter(BOARDS.keys()))
        self.column_name = "To-do"

    @discord.ui.select(
        placeholder="Change Board (Default: Your Team)",
        options=[SelectOption(label=name, value=id) for name, id in BOARDS.items()],
        row=0
    )
    async def select_board(self, interaction: Interaction, select: discord.ui.Select):
        self.board_id = select.values[0]
        self.board_name = [name for name, id in BOARDS.items() if id == self.board_id][0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Select Column (Default: To-do)",
        options=[SelectOption(label=col, value=col) for col in COLUMN_NAMES],
        row=1
    )
    async def select_column(self, interaction: Interaction, select: discord.ui.Select):
        self.column_name = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="Go to Details", style=discord.ButtonStyle.success, row=2)
    async def open_modal(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CardModal(self.board_name, self.board_id, self.column_name))

# --- Slash Commands ---

@bot.tree.command(name="st_setup", description="Link your Discord account to Superthread")
async def st_setup(interaction: Interaction):
    logger.info(f"Received /st_setup from {interaction.user}")
    view = SetupWizard(interaction.user.id)
    embed = Embed(
        title="🛡️ GDSCommander Secure Linking",
        description=(
            "To automate tasks and reports, we need to link your Discord account to your Superthread identity.\n\n"
            "**How to find your User ID:**\n"
            "1. Open Superthread in your browser.\n"
            "2. Click your **Profile Image** (bottom left).\n"
            "3. Select **Profile Settings**.\n"
            "4. Copy your **User ID** (starts with 'u...').\n\n"
            "*We use this ID to identify you when creating cards.*"
        ),
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="st_create", description="Create a new card in Superthread")
async def st_create(interaction: Interaction):
    logger.info(f"Received /st_create from {interaction.user}")
    config = get_user_config(interaction.user.id)
    if not config:
        await interaction.response.send_message(
            "❌ **Account Not Linked!**\nUse `/st_setup` first to link your Superthread ID.", 
            ephemeral=True
        )
        return
    view = CardCreationView(config)
    await interaction.response.send_message(
        "### 📝 Create a task\nConfigure the destination below:", 
        view=view, 
        ephemeral=True
    )
