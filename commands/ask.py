'''/ask, questions about the club answered by gemini'''
import asyncio
import logging
import time
from os import getenv

import discord
from discord import app_commands
from google.genai import errors

from setup import bot
from config import ASK_CATEGORY_IDS, ASK_COOLDOWN
from database import first_ask
from ai.gemini import answer
from ai.rag import retrieve

logger = logging.getLogger("GDSCommander.ask")

NOTICE = ("Heads up: /ask runs on Google's Gemini free tier, so Google can use your questions and the answers "
          "to improve its products, including training its AI. Don't put anything private or personal in here. "
          "You'll only see this once.")

last_asked = {}  # user id -> when they last asked


async def build_reply(question):
    header = f"> {question}\n"  # discord doesn't show what was asked, so quote it
    try:
        chunks = await retrieve(question)
        text = await asyncio.wait_for(answer(question, chunks), timeout=30)
    except Exception as error:
        logger.exception("Couldn't answer /ask")
        if isinstance(error, errors.APIError) and error.code == 429:
            return header + "I'm out of free AI quota for now, try again later."
        return header + "Couldn't get an answer right now, try again in a bit."
    if not text:
        return header + "I couldn't come up with an answer, try asking it differently."
    sources = ", ".join(dict.fromkeys(chunk.source for chunk in chunks))  # drops repeats, keeps the order
    footer = f"\n-# sources: {sources}" if sources else ""
    # discord caps messages at 2000 characters
    return header + text[:2000 - len(header) - len(footer)] + footer


@bot.tree.command(name="ask", description="Ask the bot something!")
@app_commands.guild_only()
@app_commands.describe(question="What do you want to know?")
async def ask(interaction: discord.Interaction, question: app_commands.Range[str, 1, 300]):
    if interaction.channel.category_id not in ASK_CATEGORY_IDS:
        await interaction.response.send_message("You can't use /ask here yet.", ephemeral=True)
        return
    if not getenv("GEMINI_API_KEY"):
        await interaction.response.send_message("/ask isn't set up yet, the bot has no Gemini key.", ephemeral=True)
        return
    wait = last_asked.get(interaction.user.id, 0) + ASK_COOLDOWN - time.monotonic()
    if wait > 0:
        await interaction.response.send_message(f"Slow down! You can ask again in {wait:.0f}s.", ephemeral=True)
        return
    last_asked[interaction.user.id] = time.monotonic()

    # everyone sees "GDSCommander is thinking...", then the answer replaces it
    await interaction.response.defer(thinking=True)
    await interaction.edit_original_response(content=await build_reply(question), allowed_mentions=discord.AllowedMentions.none())
    # after the answer on purpose, the first followup would replace the thinking message instead
    if first_ask(interaction.user.id):
        await interaction.followup.send(NOTICE, ephemeral=True)
