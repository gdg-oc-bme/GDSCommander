'''Entrypoint'''
from os import getenv
from dotenv import load_dotenv
import threading
import logging
import sys

# Standardized logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GDSCommander")

def main():
    logger.info("------------------------------------------")
    logger.info("GDSCommander Starting Up...")
    logger.info("------------------------------------------")
    
    if getenv("ENV")!="PROD":
        load_dotenv()
        logger.info(".env file loaded.")

    from setup import bot
    
    # We import ALL command modules to trigger their decorators
    logger.info("Importing Commands...")
    from commands import help, teams, join, about, socials, createRole, techTrivia, event, superthread, meeting
    
    # We import Events
    import events
    from events import welcomemessage, nameChange, logReminder
    
    logger.info("Initializing Database...")
    from database import init_db, list_user_mappings
    init_db()
    
    # Database Validation Print
    mappings = list_user_mappings()
    if not mappings:
        logger.info("Database validation: No user mappings found yet.")
    else:
        logger.info(f"Database validation: Found {len(mappings)} user mappings:")
        for m in mappings:
            logger.info(f"  - Discord: {m[0]} | Email: {m[1]} | ST ID: {m[2]} | Board: {m[3]}")
    
    # api.py was never committed; start the bridge only if the file is present
    try:
        from api import run_api
    except ModuleNotFoundError as e:
        if e.name != "api":
            raise
        logger.warning("api.py not found, skipping FastAPI bridge.")
    else:
        logger.info("Starting FastAPI bridge thread...")
        api_thread = threading.Thread(target=run_api, args=(bot,), daemon=True)
        api_thread.start()

    TOKEN=getenv("TOKEN")
    logger.info("Connecting to Discord...")
    bot.run(TOKEN)

if __name__=="__main__":
    main()
