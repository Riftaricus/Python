import os
import discord
import asyncio
from dotenv import load_dotenv
from bot import Bot

def run():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    intents = discord.Intents.default()

    class MyClient(discord.Client):
        async def setup_hook(self):
            self.bot_logic = Bot(self)
            await self.bot_logic.setup()

    client = MyClient(intents=intents)
    client.run(token)

if __name__ == "__main__":
    run()