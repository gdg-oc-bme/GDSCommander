from discord.ext import commands
import discord

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(f"!!! GDSCOMMANDER IS ONLINE: {bot.user} !!!")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    
    # Syncing to every guild the bot is in for INSTANT updates
    print("Forcing Guild Sync for instant command updates...")
    for guild in bot.guilds:
        try:
            # We copy the global tree to the guild and sync it
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"--- Synced {len(synced)} commands to Guild: {guild.name} ({guild.id}) ---")
        except Exception as e:
            print(f"Failed to sync to {guild.name}: {e}")
    
    # Also sync global (just in case)
    await bot.tree.sync()
    print("Global sync complete.")
