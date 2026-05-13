import asyncio
import json
import os
import discord
from discord.ext import tasks
from io import BytesIO
import requests
from dotenv import load_dotenv


URL = "https://cataas.com/cat"
load_dotenv()

class CatBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.targets = []
    
    async def on_ready(self):
        print(f'Logged in as {self.user}', flush=True)
        # Load targets
        script_dir = os.path.dirname(os.path.abspath(__file__))
        targets_path = os.path.join(script_dir, "Targets.json")
        with open(targets_path, "r") as file:
            data = json.load(file)
            self.targets = data['targets']
        
        # Start the send_cats task if not already running
        if not self.send_cats.is_running():
            self.send_cats.start()
    
    @tasks.loop(hours=1)
    async def send_cats(self):
        """Send random cat pictures to target channel"""
        channel = self.get_channel(1504036702795071508)
        if not channel:
            print("Channel not found", flush=True)
            return
        
        try:
            # Fetch cat image
            response = requests.get(URL)
            if response.status_code == 200:
                cat_image = BytesIO(response.content)
                cat_image.seek(0)
                await channel.send(f"Here's a random cat! 🐱", 
                                  file=discord.File(cat_image, filename="cat.jpg"))
                print(f"Sent cat to channel {channel.name}", flush=True)
        except discord.Forbidden:
            print(f"Cannot send message to channel - permission denied", flush=True)
        except discord.NotFound:
            print(f"Channel not found", flush=True)
        except Exception as e:
            print(f"Error sending cat: {type(e).__name__}: {e}", flush=True)
    
    @send_cats.before_loop
    async def before_send_cats(self):
        await self.wait_until_ready()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set", flush=True)
        exit(1)
    
    client = CatBot()
    client.run(token)