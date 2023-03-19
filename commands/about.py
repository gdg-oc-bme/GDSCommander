'''/about command implementation'''
from discord import Interaction, Embed, Color
from setup import bot

@bot.tree.command(name='about')
async def about(interaction: Interaction):
    response = Embed(
        description='''Google Developer Student Club BME is a club where techy people get to meet each other and learn new technologies.
        It is meant to bridge the gap between theory and practice and provide a welcoming community to like-minded people.''',
        color=Color.light_embed()
    )
    response.set_author(name='About GDSC BME', icon_url='https://i.imgur.com/kLnSlU2.png')
    await interaction.response.send_message(embed=response)
