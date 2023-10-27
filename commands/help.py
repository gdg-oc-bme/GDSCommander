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
    response.add_field(name='`/join`', value='You can use this with core or member as an argument to see how to join as those', inline=False)
    response.add_field(name='`/event-team`', value='Tells you about the event team responsibilities', inline=False)
    response.add_field(name='`/solutions-team`', value='Tells you about the solutions team responsibilities', inline=False)
    response.add_field(name='`/tech-team`', value='Tells you about the tech team responsibilities', inline=False)
    response.add_field(name='`/social-media-team`', value='Tells you about the social media team responsibilities', inline=False)
    response.add_field(name='`/instagram`', value='Gives you the link to our instagram account', inline=False)
    response.add_field(name='`/facebook`', value='Gives you the link to our facebook page', inline=False)
    response.add_field(name='`/linkedin`', value='Gives you the link to our linkedin account', inline=False)
    response.add_field(name='`/website`', value='Gives you the link to our website', inline=False)
    response.add_field(name='`/linktree`', value='Gives you the link to our linktree', inline=False)
    await interaction.response.send_message(embed=response)
