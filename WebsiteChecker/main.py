import json
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from website import Website

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITES_PATH = os.path.join(BASE_DIR, "Websites.json")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1504103754453090454

intents = discord.Intents.default()
bot = discord.Client(intents=intents)


def load_websites() -> list[dict]:
    with open(WEBSITES_PATH, 'r') as f:
        return json.load(f)


def check_websites() -> list[dict]:
    results = []
    for entry in load_websites():
        web = Website(entry['url'])
        result = web.ping()
        results.append({
            "name": entry['name'],
            "url": entry['url'],
            "up": result.ok,
            "reason": result.reason,
            "error": result.error,
            "elapsed": result.elapsed,
        })
    return results


def build_status_embed(results: list[dict]) -> discord.Embed:
    up = [r for r in results if r['up']]
    down = [r for r in results if not r['up']]

    embed = discord.Embed(
        title="🌐 Website Status Report",
        color=discord.Color.green() if not down else discord.Color.red(),
    )

    if up:
        embed.add_field(
            name=f"✅ Online ({len(up)})",
            value="\n".join(
                f"**{r['name']}** — {r['reason']} ({r['elapsed'].total_seconds() * 1000:.0f}ms)"
                for r in up
            ),
            inline=False,
        )

    if down:
        embed.add_field(
            name=f"❌ Offline ({len(down)})",
            value="\n".join(
                f"**{r['name']}** — {r['error'] or r['reason']}"
                for r in down
            ),
            inline=False,
        )

    embed.set_footer(text=f"Checked {len(results)} sites")
    return embed


@tasks.loop(minutes=10)
async def scheduled_check():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel {CHANNEL_ID} not found")
        return
    results = check_websites()
    await channel.send(embed=build_status_embed(results))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    scheduled_check.start()


bot.run(TOKEN)