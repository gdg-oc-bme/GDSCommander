'''Implementation of howto commands.'''
from discord import Interaction, Embed, Color
from setup import bot

@bot.tree.command(name='howto-join-member')
async def member(interaction: Interaction):
    response = Embed(
        title="How to be a member",
        description='''If you are reading this, then congrats! You are a member already!
        If you are asking for a friend, here are the steps:
        ''',
        color=Color.dark_grey()
    )
    response.add_field(
        name='Step 1', 
        value='Visit our website at https://gdsc.community.dev/budapest-university-of-technology-and-economics/',
        inline=False)
    response.add_field(name='Step 2', value='Click join', inline=False)
    response.add_field(
        name='Step 3', 
        value='We will send you an email with the discord invite. You can join the GDSC BME community!',
        inline=False)
    response.set_footer(text="We are happy to have you here :)")
    await interaction.response.send_message(embed=response)

@bot.tree.command(name='howto-join-core')
async def core(interaction: Interaction):
    response = Embed(
        title="How to be a core member",
        description='''Being a core member comes with a set of responsibilities, so you will need to go through an interview process.
        ''',
        color=Color.darker_grey()
    )
    response.add_field(
        name='When to apply', 
        value='''Recruitment usually happens in October. 
        Sometimes, a member might leave unexpectedly and we can open a position during the year, but this is less frequent.
        If you want to stay updated, follow our social media accounts and our announcements channel on Discord.''',
        inline=False)
    response.add_field(
        name='How to apply', 
        value='''The first step of the application process is a form that you will have to fill.
        The form will help us know about your background and interests. 
        If you get accepted after that stage, you will be invited to an interview with some of our leads.
        If the interview goes well, you will be welcomed as a core member!''', 
        inline=False)
    response.add_field(
        name='About the interview', 
        value='''The interview will be simple and short. It is an opportunity for us to get to know your personnality, your achievements and your interests as well as your availability.
        Competition is usually high, so don't be discouraged if you don't get accepted, you are still considered a member!''',
        inline=False)
    await interaction.response.send_message(embed=response)
