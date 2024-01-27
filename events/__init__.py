'''Event implementation'''
from setup import bot

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    # This try catch is to load the slash commands
    try: 
        synced = await bot.tree.sync()
        print(f"sync {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    if message.author == bot.user:
        return
    
    if message.mention_everyone:
        return
    
    if bot.user.mentioned_in(message):
        await message.channel.send('You pinged me! I\'m still a work in progress!')
    