'''Event implementation'''
from setup import bot

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    if message.author == bot.user:
        return
    
    if message.mention_everyone:
        return
    
    if bot.user.mentioned_in(message):
        await message.channel.send('You pinged me! I\'m still a work in progress!')
    