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
    from commands import help, teams, join, about, socials, createRole, techTrivia, event, superthread
    
    # We import Events
    import events
    from events import welcomemessage, nameChange
    
    logger.info("Initializing Database...")
    from database import init_db
    init_db()
    
    logger.info("Starting FastAPI bridge thread...")
    from api import run_api
    api_thread = threading.Thread(target=run_api, args=(bot,), daemon=True)
    api_thread.start()

    TOKEN=getenv("TOKEN")
    logger.info("Connecting to Discord...")
    bot.run(TOKEN)

if __name__=="__main__":
    main()
