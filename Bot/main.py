from pathlib import Path

import discord
import atexit


from Bot.Modules.ClairemontBot import ShadowBot

# GLOBALS
intents = discord.Intents.default()
intents.message_content = True


if __name__ == '__main__':
    base_dir = Path(__file__).resolve().parent
    Shadow = ShadowBot(intents, directory=base_dir)
    Shadow.run()


    @atexit.register
    def killDatabases():
        Shadow.killDatabases()