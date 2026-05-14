import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import os
from dotenv import load_dotenv
from location import getLoc
from openmeteo import getData

load_dotenv()
TOKEN      = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])

intents = discord.Intents.default()
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

weather_message = None  # stores the single message we keep editing


def build_weather_message():
    lat, long = getLoc()
    data = getData(lat, long)

    hourly     = data["hourly"]
    temps      = hourly["temperature_2m"]
    humidities = hourly["relative_humidity_2m"]
    winds      = hourly["wind_speed_10m"]

    current      = data["current"]
    current_temp = current["temperature_2m"]
    current_wind = current["wind_speed_10m"]

    return (
        f"🌤️ **Daily Weather Report**\n\n"
        f"**Current conditions**\n"
        f"  🌡️ Temperature: {current_temp}°C\n"
        f"  💨 Wind speed:  {current_wind} km/h\n\n"
        f"**Today's forecast ({len(temps)} hours)**\n"
        f"  🌡️ Temperature — max: {max(temps)}°C, min: {min(temps)}°C, avg: {sum(temps)/len(temps):.1f}°C\n"
        f"  💧 Humidity    — max: {max(humidities)}%, min: {min(humidities)}%, avg: {sum(humidities)/len(humidities):.1f}%\n"
        f"  💨 Wind speed  — max: {max(winds)} km/h, min: {min(winds)} km/h, avg: {sum(winds)/len(winds):.1f} km/h\n"
    )


async def update_weather():
    global weather_message

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel {CHANNEL_ID} not found.")
        return

    content = build_weather_message()

    if weather_message is None:
        # First run — send a new message and save it
        weather_message = await channel.send(content)
        print(f"Weather message created (id: {weather_message.id})")
    else:
        # Subsequent runs — edit the existing message
        await weather_message.edit(content=content)
        print("Weather message updated.")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    scheduler.add_job(
        update_weather,
        CronTrigger(minute=2),
        id="daily_weather",
        replace_existing=True
    )
    scheduler.start()
    print("Scheduler started")

    await update_weather()



bot.run(TOKEN)