import discord
from discord import Interaction, app_commands, ui
from setup import bot
import asyncio
import re
from fuzzywuzzy import process
from datetime import datetime, timedelta
#pip install fuzzywuzzy
#pip install python-Levenshtein
#pip install datetime


def parse_event_time(time_str):
    # Define the expected date-time format, e.g., "March 5, 2024 15:00"
    date_format = "%B %d, %Y %H:%M"

    try:
        # Parse the date-time string into a datetime object
        event_time = datetime.strptime(time_str, date_format)
    except ValueError as e:
        print(f"Could not parse the event time: {e}")
        return None
    
    return event_time

def format_delta(delta):
    # Get the total seconds in the timedelta object
    seconds = int(delta.total_seconds())
    
    # Helper function to divide seconds
    def get_time_unit(unit_seconds):
        return seconds // unit_seconds, seconds % unit_seconds
    
    # Calculate days, hours, minutes, and seconds
    days, seconds = get_time_unit(86400)  # 60 * 60 * 24
    hours, seconds = get_time_unit(3600)  # 60 * 60
    minutes, seconds = get_time_unit(60)

    # Format the string based on the largest time unit available
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

class EventModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(title="Create an Event", *args, **kwargs)
        
        self.add_item(discord.ui.InputText(label="Event Name", placeholder="Name of the event"))
        self.add_item(discord.ui.InputText(label="Time", placeholder="Ex: March 5, 2024 15:00"))
        self.add_item(discord.ui.InputText(label="Location", placeholder="Physical or virtual location"))
        self.add_item(discord.ui.InputText(label="Description", style=discord.InputTextStyle.paragraph))

    async def callback(self, interaction: discord.Interaction):
        event_name = self.children[0].value
        time = self.children[1].value
        location = self.children[2].value
        description = self.children[3].value

        event_datetime = parse_event_time(time)

        if event_datetime is None:
            await interaction.response.send_message(
                "Failed to parse the event time. Please use the format 'Month Day, Year Hour:Minute', for example, 'March 5, 2024 15:00'.",
                ephemeral=True
            )
            return

        embed = discord.Embed(title=event_name, description=description, color=discord.Color.blue())
        embed.add_field(name="Time", value=time)
        embed.add_field(name="Location", value=location)
        embed.set_footer(text="Event ID: XYZ")

        await interaction.response.send_message(embed=embed)

        # Start the countdown task
        countdown_task = asyncio.create_task(
            update_event_countdown(interaction, event_datetime)
        )

async def update_event_countdown(interaction, event_datetime):
    event_message = await interaction.original_response()
    while True:
        now = datetime.utcnow()
        delta = event_datetime - now
        if delta.total_seconds() <= 0:
            await event_message.edit(content="The event has started!", embed=None)
            break
        else:
            new_embed = event_message.embeds[0].set_footer(text=f"Event starts in: {format_delta(delta)}")
            await event_message.edit(embed=new_embed)
            await asyncio.sleep(60)  # Update every minute

@bot.tree.command(name='event', description="Create a new event")
async def event(interaction: discord.Interaction):
    modal = EventModal()
    await interaction.response.send_modal(modal)