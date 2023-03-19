'''Implementation of commands related to the different teams'''
from discord import Interaction, Embed, Color
from setup import bot

@bot.tree.command(name='event-team')
async def event_team(interaction: Interaction):
    response = Embed(
        description='''
            The event team is the team that handles events (as the name suggests).
            The following items are the responsibilities of each event team member.
        ''',
        color=Color.blue()
    )
    response.set_author(name='About the Event Team', icon_url='https://i.imgur.com/8mhlomF.png')
    response.add_field(
        name='Meetings', 
        value='''This includes setting a time that matches everyone's schedule and choosing the place of the meeting''', 
        inline=False)
    response.add_field(
        name='Team buildings', 
        value='''Event team members should be fun to be around and thus they are the ones who organize fun games for the core team''', 
        inline=False)
    response.add_field(
        name='Events', 
        value='''The event team handles the booking of rooms for the different events, choosing suitable dates and welcoming guests on the day of the event''', 
        inline=False)
    await interaction.response.send_message(embed=response)
    
@bot.tree.command(name='solutions-team')
async def solutions_team(interaction: Interaction):
    response = Embed(
        description='''
            The solutions team represents the HR team of the club.
            The following items are the responsibilities of each solutions team member.
        ''',
        color=Color.green()
    )
    response.set_author(name='About the Solutions Team', icon_url='https://i.imgur.com/tynviZ5.png')
    response.add_field(
        name='Sprakers and Sponsors', 
        value='''Members of the solutions team are resourceful and easy-going. They are comfotable talking to strangers and inviting them to help the club during events''', 
        inline=False)
    response.add_field(
        name='Recruitment', 
        value='''The solutions team is also responsible for recruitment and team evaluation. They help the leads make decisions about who gets to join the club''', 
        inline=False)
    response.add_field(
        name='Problem Solving', 
        value='''In case the club is having internal problems, the solutions team is there to solve them. I am one of those solutions beep! :D''', 
        inline=False)
    await interaction.response.send_message(embed=response)

@bot.tree.command(name='tech-team')
async def tech_team(interaction: Interaction):
    response = Embed(
        description='''
            The tech team is the team that comes up with fun event ideas and researches them.
            The following items are the responsibilities of each tech team member.
        ''',
        color=Color.yellow()
    )
    response.set_author(name='About the Tech Team', icon_url='https://i.imgur.com/iUIyZIz.png')
    response.add_field(
        name='Research', 
        value='''Tech team members are curious and smart. They should be able to research new interesting technologies and suggest fun event ideas to the rest of the club''', 
        inline=False)
    response.add_field(
        name='Presentations', 
        value='''A tech team member should be comfortable enough to give talks and mentor other members during events.''', 
        inline=False)
    response.add_field(
        name='IT Support', 
        value='''The tech team is also responsible for tech support during events. For example, if the event is online, they are the ones who should set up the platform.''', 
        inline=False)
    await interaction.response.send_message(embed=response)

@bot.tree.command(name='social-media-team')
async def social_media_team(interaction: Interaction):
    response = Embed(
        description='''
            The social media team is the team that handles social media (as the name suggests).
            The following items are the responsibilities of each social media team member.
        ''',
        color=Color.red()
    )
    response.set_author(name='About the Social Media Team', icon_url='https://i.imgur.com/TMJTWeZ.png')
    response.add_field(
        name='Promotion', 
        value='''Social media team members are modern and creative. They should be able to use social media platforms easily and should be available enough for communicating with external members''', 
        inline=False)
    response.add_field(
        name='Design', 
        value='''Google has strict branding guides. Social media members have to unleash their creativity when designing posters and stories while sticking to the brand colors''', 
        inline=False)
    response.add_field(
        name='Content', 
        value='''The social media team should ensure the involvement of audience by providing interesting content from time to time''', 
        inline=False)
    await interaction.response.send_message(embed=response)
    