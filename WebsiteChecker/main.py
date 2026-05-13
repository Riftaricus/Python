import json
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from website import Website

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITES_PATH = os.path.join(BASE_DIR, "Websites.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1504103754453090454

intents = discord.Intents.default()
bot = discord.Client(intents=intents)


def load_websites() -> list[dict]:
    with open(WEBSITES_PATH, 'r') as f:
        return json.load(f)


def load_state() -> dict:
    """Load previous state. Returns {url: up} mapping."""
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_state(state: dict) -> None:
    """Save current state to file."""
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f)


def get_changes(results: list[dict], previous_state: dict) -> dict:
    """
    Compare current results with previous state.
    Returns {url: {"name": name, "old": bool, "new": bool}} for changed sites.
    """
    changes = {}
    for result in results:
        url = result['url']
        current_up = result['up']
        previous_up = previous_state.get(url)
        
        if previous_up is not None and previous_up != current_up:
            changes[url] = {
                "name": result['name'],
                "old": previous_up,
                "new": current_up,
            }
    return changes


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


def build_changes_embed(changes: dict) -> discord.Embed:
    """Build an embed showing only changed websites."""
    ups = [v for v in changes.values() if v['new']]
    downs = [v for v in changes.values() if not v['new']]

    embed = discord.Embed(
        title="🔔 Website Status Changed",
        color=discord.Color.orange(),
    )

    if ups:
        embed.add_field(
            name=f"✅ Back Online ({len(ups)})",
            value="\n".join(f"**{v['name']}**" for v in ups),
            inline=False,
        )

    if downs:
        embed.add_field(
            name=f"❌ Went Down ({len(downs)})",
            value="\n".join(f"**{v['name']}**" for v in downs),
            inline=False,
        )

    return embed


@tasks.loop(minutes=10)
async def scheduled_check():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel {CHANNEL_ID} not found")
        return
    
    # Load previous state
    previous_state = load_state()
    
    # Check websites
    results = check_websites()
    
    # Find changes
    changes = get_changes(results, previous_state)
    
    # Only send message if there are changes
    if changes:
        await channel.send(embed=build_changes_embed(changes))
        print(f"Website status changes detected: {list(changes.keys())}")
    else:
        print("Website status check: No changes")
    
    # Save current state for next check
    new_state = {result['url']: result['up'] for result in results}
    save_state(new_state)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    scheduled_check.start()


bot.run(TOKEN)