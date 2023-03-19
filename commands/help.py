'''/help command implementation'''
from discord import Interaction, Embed, Color
from setup import bot

@bot.tree.command(name='help')
async def help(interaction: Interaction):
    response = Embed(
        title="GDSCommander Help",
        description='These are the slash commands you will need while using this bot:',
        color=Color.light_embed()
    )
    response.set_thumbnail(url='https://i.imgur.com/kLnSlU2.png')
    response.set_footer(text="Hope it helped :)")
    
    response.add_field(name='`/help`', value='Shows you the available commands', inline=False)
    response.add_field(name='`/about`', value='Shows you a short introduction about the club', inline=False)
    response.add_field(name='`/howto-join-member`', value='Tells you how to join as a member', inline=False)
    response.add_field(name='`/howto-join-core`', value='Tells you how to join as a core member', inline=False)
    response.add_field(name='`/event-team`', value='Tells you about the event team responsibilities', inline=False)
    response.add_field(name='`/solutions-team`', value='Tells you about the solutions team responsibilities', inline=False)
    response.add_field(name='`/tech-team`', value='Tells you about the tech team responsibilities', inline=False)
    response.add_field(name='`/social-media-team`', value='Tells you about the social media team responsibilities', inline=False)
    await interaction.response.send_message(embed=response)
