import discord
from discord.ext import commands
from discord import Interaction, Embed, Color
from setup import bot

@bot.event
async def on_member_join(member):
    print(f"Recognized that {member.name} joined")
    channel = member.guild.get_channel(881623399733014550)
    if channel:
        welcome_message = f'''Welcome to the server, {member.mention}! We're more than happy to have you here! 😁
You can use /help for a list of available commands.'''
        await channel.send(welcome_message)
        print(f"Sent a welcome message to {member.name} on the server.")
    new_user_message = '''Welcome to GDSC BME!
Google Developer Student Club BME is a club where techy people get to meet each other and learn new technologies. 
We intend to bridge the gap between theory and practice and provide a welcoming community to like-minded people.
If you have any questions, don't hesitate to ask any core-team member.
Make sure to go through the rules & description of every channel before posting.
Lastly, don't forget to introduce yourself in the #self-introductions channel! 😊'''
    try:
        await member.send(new_user_message)
        print(f"Sent a welcome message to {member.name} privately.")
    except Exception as e:
        print(f"Couldn't message {member.name}: {e}")

@bot.event
async def on_member_remove(member):
    print(f"Recognized that {member.name} left")
    channel = member.guild.get_channel(881623399733014550)
    if channel:
        farewell_message = f"Goodbye {member.name} 😔! It was great having you. See you again soon!"
        await channel.send(farewell_message)
