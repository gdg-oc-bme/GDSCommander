from discord import Interaction, Embed, Color
from setup import bot
import requests
import random
import html

API_URL = 'https://opentdb.com/api.php'

@bot.tree.command(name='techtrivia')
async def techtrivia(interaction: Interaction):
    # Parameters for API request
    params = {
        'amount': 1,            
        'category': 18,         
        'type': 'multiple'      
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    if data['response_code'] == 0:  
        question = data['results'][0]['question']
        correct_answer = data['results'][0]['correct_answer']
        incorrect_answers = data['results'][0]['incorrect_answers']
        answers = incorrect_answers + [correct_answer]
        random.shuffle(answers)
        
        question = html.unescape(question)
        answers = [html.unescape(answer) for answer in answers]
        correct_answer = html.unescape(correct_answer)
        
        formatted_question = f"**Question:** {question}\n"
        formatted_answers = '\n'.join([f"{index+1}. {answer}" for index, answer in enumerate(answers)])
        response = Embed(
            title='Tech Trivia',
            description=formatted_question + "\n**Answers:**\n" + formatted_answers,
            color=Color.blue()
        )
        response.set_author(name='Tech Trivia Bot', icon_url='https://i.imgur.com/kLnSlU2.png')
        response.set_footer(text='Powered by Open Trivia Database')

        await interaction.response.send_message(embed=response)
        
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        user_response = await bot.wait_for('message', check=check)        
        if user_response.content.lower() == correct_answer.lower():
            await interaction.followup.send('Congratulations! You answered correctly!')
        else:
            await interaction.followup.send(f'Incorrect answer. The correct answer is: {correct_answer}')
    else:
        await interaction.response.send_message(content="Failed to fetch trivia question.")