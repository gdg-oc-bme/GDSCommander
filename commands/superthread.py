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

# --- Superthread API Helpers ---
SUPERTHREAD_TOKEN = os.getenv("PERSONAL_API_TOKEN_SUPERTHREAD")
HEADERS = {
    "Authorization": f"Bearer {SUPERTHREAD_TOKEN}",
    "Accept": "application/json"
}

def fetch_st_user_id(email):
    """Try to find the Superthread user ID by email with deep search."""
    url = f"https://api.superthread.com/v1/{TEAM_ID}/members"
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            members = resp.json()
            for m in members:
                # Check top level
                if m.get('email') == email:
                    return m.get('id')
                # Check nested user object (common in Superthread)
                user_obj = m.get('user', {})
                if user_obj.get('email') == email:
                    return user_obj.get('id') or m.get('id')
    except Exception as e:
        logger.error(f"Error fetching members: {e}")
    return None

# --- UI Components ---

class SetupWizard(View):
    def __init__(self, discord_id):
        super().__init__(timeout=180)
        self.discord_id = discord_id
        self.email = None
        self.user_id = None

    @discord.ui.button(label="1. Search by Email", style=discord.ButtonStyle.primary)
    async def link_email(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EmailModal(self))

    @discord.ui.button(label="2. Enter User ID Manually", style=discord.ButtonStyle.secondary)
    async def manual_id(self, interaction: Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ManualIDModal(self))

class EmailModal(Modal, title="Link Superthread Email"):
    email = TextInput(label="Superthread Email", placeholder="your@email.com")

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: Interaction):
        email_val = self.email.value
        user_id = fetch_st_user_id(email_val)
        
        if not user_id:
            logger.warning(f"Email not found: {email_val}. Offering manual ID.")
            await interaction.response.send_message(
                f"❌ Could not find a member with email `{email_val}`.\n\n"
                "Tip: Make sure you are a member of the workspace. If it still fails, use the **'Enter User ID Manually'** button.", 
                ephemeral=True
            )
            return
        
        self.parent_view.email = email_val
        self.parent_view.user_id = user_id
        view = BoardSelectView(self.parent_view)
        await interaction.response.send_message(f"✅ Found you (ID: `{user_id}`)! Now select your primary Team/Board:", view=view, ephemeral=True)

class ManualIDModal(Modal, title="Enter Superthread User ID"):
    user_id = TextInput(label="User ID", placeholder="Starts with 'u', e.g. uRsze...")
    email_label = TextInput(label="Confirm Email (Optional)", required=False)

    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    async def on_submit(self, interaction: Interaction):
        self.parent_view.user_id = self.user_id.value
        self.parent_view.email = self.email_label.value or "Manual Linked"
        view = BoardSelectView(self.parent_view)
        await interaction.response.send_message(f"✅ ID Set! Now select your primary Team/Board:", view=view, ephemeral=True)

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
        save_user_mapping(self.parent_view.discord_id, self.parent_view.email, self.parent_view.user_id, board_id)
        await interaction.response.send_message(f"✅ Done! You are linked to `{board_name}` as User `{self.parent_view.user_id}`.", ephemeral=True)

# --- Card Creation ---

class CardModal(Modal, title="Create Superthread Card"):
    card_title = TextInput(label="Title")
    card_desc = TextInput(label="Description", style=discord.TextStyle.paragraph, required=False)

    def __init__(self, board_name, board_id, column_name):
        super().__init__()
        self.board_name = board_name
        self.board_id = board_id
        self.column_name = column_name

    async def on_submit(self, interaction: Interaction):
        column_id = get_column_id(self.board_id, self.column_name)
        payload = {
            "title": self.card_title.value,
            "content": self.card_desc.value or "",
            "board_id": self.board_id,
            "list_id": column_id
        }
        url = f"{BASE_URL}/{TEAM_ID}/cards"
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code in [200, 201]:
            embed = Embed(title="✅ Card Created!", color=discord.Color.green())
            embed.add_field(name="Title", value=self.card_title.value, inline=False)
            embed.add_field(name="Board", value=self.board_name, inline=True)
            embed.add_field(name="Column", value=self.column_name, inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ Error: {response.status_code}", ephemeral=True)

class CardCreationView(View):
    def __init__(self, user_config):
        super().__init__(timeout=120)
        self.board_id = user_config.get('board_id')
        self.board_name = [name for name, id in BOARDS.items() if id == self.board_id][0] if self.board_id else next(iter(BOARDS.keys()))
        self.column_name = "To-do"

    @discord.ui.select(
        placeholder="Change Board",
        options=[SelectOption(label=name, value=id) for name, id in BOARDS.items()],
        row=0
    )
    async def select_board(self, interaction: Interaction, select: discord.ui.Select):
        self.board_id = select.values[0]
        self.board_name = [name for name, id in BOARDS.items() if id == self.board_id][0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Select Column",
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

@bot.tree.command(name="st_setup", description="Start the Superthread configuration wizard")
async def st_setup(interaction: Interaction):
    logger.info(f"Received /st_setup from {interaction.user}")
    view = SetupWizard(interaction.user.id)
    embed = Embed(
        title="🤖 GDSCommander Configuration Wizard",
        description="Let's link your Discord account to Superthread to enable automation.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="st_create", description="Create a new card in Superthread interactively")
async def st_create(interaction: Interaction):
    logger.info(f"Received /st_create from {interaction.user}")
    config = get_user_config(interaction.user.id)
    if not config:
        await interaction.response.send_message("❌ Setup first with `/st_setup`.", ephemeral=True)
        return
    view = CardCreationView(config)
    await interaction.response.send_message("Configure your card destination:", view=view, ephemeral=True)
