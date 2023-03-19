'''Entrypoint'''
from os import getenv
from dotenv import load_dotenv

def main():
    # In case it is a production environment, the .env file should be ignored
    # Variables in production should be stored somewhere else (e.g. GitHub secrets)
    if getenv("ENV")!="PROD":
        load_dotenv()
    from setup import bot

    from commands import help, teams
    import events
    TOKEN=getenv("TOKEN")
    bot.run(TOKEN)

if __name__=="__main__":
    main()
