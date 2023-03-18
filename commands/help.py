'''/help command implementation'''
from discord import Interaction, Embed, Color
from setup import bot

@bot.tree.command(name='help')
async def help(interaction: Interaction):
    response = Embed(
        title="GDSCommander Help",
        description='These are the slash commands you will need while using this bot:',
        color=Color.blue()
    )
    response.set_footer(text="Hope it helped :)")
    response.add_field(name='/help', value='Shows you the available commands', inline=False)
    response.set_thumbnail(url='https://i.imgur.com/kLnSlU2.png')
    await interaction.response.send_message(embed=response)
