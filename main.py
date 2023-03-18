import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    if message.author == client.user:
        return
    
    if client.user.mentioned_in(message):
        await message.channel.send('You pinged me! I\'m still a work in progress!')

@bot.tree.command()
async def test(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is a slash command!")

def main():
    # In case it is a production environment, the .env file should be ignored
    # Variables in production should be stored somewhere else (e.g. GitHub secrets)
    if os.getenv("ENV")!="PROD":
        load_dotenv()
        
    TOKEN=os.getenv("TOKEN")
    bot.run(TOKEN)
    client.run(TOKEN)

if __name__=="__main__":
    main()
