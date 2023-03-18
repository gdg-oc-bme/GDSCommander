import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
    
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    # This try catch is to load the slash commands
    try: 
        synced = await bot.tree.sync()
        print(f"sync {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name='help')
async def help(interaction: discord.Interaction):
    response = discord.Embed(
        title="GDSCommander Help",
        description='These are the slash commands you will need while using this bot:',
        color=discord.Color.blue()
    )
    response.set_footer(text="Hope it helped :)")
    response.add_field(name='/help', value='Shows you the available commands', inline=False)

    await interaction.response.send_message(embed=response)
    
@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    if message.author == bot.user:
        return
    
    if bot.user.mentioned_in(message):
        await message.channel.send('You pinged me! I\'m still a work in progress!')
    
def main():
    # In case it is a production environment, the .env file should be ignored
    # Variables in production should be stored somewhere else (e.g. GitHub secrets)
    if os.getenv("ENV")!="PROD":
        load_dotenv()
        
    TOKEN=os.getenv("TOKEN")
    bot.run(TOKEN)

if __name__=="__main__":
    main()
