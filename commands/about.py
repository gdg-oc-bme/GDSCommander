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
    response.add_field(
        name='General structure', 
        value='''The club is divided into members and core members.
        - *Members* get to hear about the latest events and announcements of the club and of Google. They also get to be part of a community inside the university by joining the Discord server.
        - *Core members* are responsible for keeping the club alive and for creating events. They get to choose what goes on inside the club and they can contribute to the clubs internal projects.''', 
        inline=False)
    response.add_field(
        name='Core Team structure', 
        value='''The core team structure is divided into 4 teams and a lead (or co-leads).
        The different teams are the event team, the solutions team, the tech team and the social media team. 
        You can get to know these teams better by typing `/event-team`, `/solutions-team`, `/tech-team`, `/social-media-team` respectively.''', 
        inline=False)
    await interaction.response.send_message(embed=response)
