'''Implementation of commands related to social media accounts'''
from discord import Interaction, Embed, Color
from setup import bot

@bot.tree.command(name='instagram')
async def instagram(interaction: Interaction):
    response = f'''
    Hey {interaction.user.mention} you just requested GDSC BME's instagram account! Here you go!
    https://www.instagram.com/gdscbme/
    You can also visit our linktree where all our social media accounts are linked.
    https://linktr.ee/gdscbme'''
    await interaction.response.send_message(response)

@bot.tree.command(name='facebook')
async def facebook(interaction: Interaction):
    response = f'''
    Hey {interaction.user.mention} you just requested GDSC BME's facebook page! Here you go!
    https://www.facebook.com/gdscbme
    You can also visit our linktree where all our social media accounts are linked.
    https://linktr.ee/gdscbme'''
    await interaction.response.send_message(response)

@bot.tree.command(name='linkedin')
async def linkedin(interaction: Interaction):
    response = f'''
    Hey {interaction.user.mention} you just requested GDSC BME's linkedin account! Here you go!
    https://www.linkedin.com/company/gdscbme/
    You can also visit our linktree where all our social media accounts are linked.
    https://linktr.ee/gdscbme'''
    await interaction.response.send_message(response)

@bot.tree.command(name='linktree')
async def linktree(interaction: Interaction):
    response = f'''
    Hey {interaction.user.mention} you just requested GDSC BME's linktree page! Here you go!
    https://linktr.ee/gdscbme'''
    await interaction.response.send_message(response)

@bot.tree.command(name='website')
async def website(interaction: Interaction):
    response = f'''
    Hey {interaction.user.mention} you just requested GDSC BME's website! Here you go!
    https://gdsc.community.dev/budapest-university-of-technology-and-economics/
    You can also visit our linktree where all our social media accounts are linked.
    https://linktr.ee/gdscbme'''
    await interaction.response.send_message(response)
