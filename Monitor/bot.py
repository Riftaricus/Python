import asyncio
import datetime
from classes import Statistics
from saving import save

STATS_CHANNEL_ID = 1503834424788389918

class Bot:
    def __init__(self, client):
        self.client = client
        self.stats_channel = None

    async def setup(self):
        self.client.loop.create_task(self.scan_loop())

    async def scan_loop(self):
        await self.client.wait_until_ready()

        self.stats_channel = await self.client.fetch_channel(STATS_CHANNEL_ID)

        while not self.client.is_closed():
            stats = Statistics()
            data = stats.get_dictionary()

            print(f"Container Scan Dated {datetime.datetime.now()}", flush=True)
            save(data)

            data = stats.get_dictionary()

            message = "📊 **Container Stats**\n\n"

            # RAM
            ram = data.get("ram", {})
            message += "🧠 **RAM**\n"
            message += f"• Total: {ram.get('total_gb')} GB\n"
            message += f"• Used: {ram.get('used_gb')} GB\n"
            message += f"• Available: {ram.get('available_gb')} GB\n"
            message += f"• Usage: {ram.get('usage_percent')}%\n\n"

            # CPU
            cpu = data.get("cpu", {})
            message += "⚙️ **CPU**\n"
            message += f"• Usage: {cpu.get('usage_percent')}%\n\n"

            # Disk
            disk = data.get("disk", {})
            message += "💾 **Disk**\n"
            message += f"• Total: {disk.get('total_gb')} GB\n"
            message += f"• Used: {disk.get('used_gb')} GB\n"
            message += f"• Free: {disk.get('free_gb')} GB\n"
            message += f"• Usage: {disk.get('usage_percent')}%\n\n"

            # Network
            net = data.get("network", {})
            message += "🌐 **Network**\n"
            message += f"• Sent: {net.get('bytes_sent')} bytes\n"
            message += f"• Received: {net.get('bytes_received')} bytes\n"

            await self.stats_channel.send(message)

            await asyncio.sleep(10)

    async def main(self):
        stats = Statistics()

        now = datetime.datetime.now()

        print(f"Container Scan Dated {now}", flush=True)
        print("History Successfully Saved!", flush=True)

        save(stats.get_dictionary())
    