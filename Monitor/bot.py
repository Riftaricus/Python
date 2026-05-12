import asyncio
import datetime
from classes import Statistics
from saving import save

RAM_THRESHOLD = 80
CPU_THRESHOLD = 80
DISK_THRESHOLD = 85

WARNING_REPEAT = 3

STATS_CHANNEL_ID = 1503834424788389918


class Bot:
    def __init__(self, client):
        self.client = client
        self.stats_channel = None

        # tracks how many times we’ve warned
        self.alert_counts = {
            "ram": 0,
            "cpu": 0,
            "disk": 0
        }

    async def setup(self):
        self.client.loop.create_task(self.scan_loop())

    async def scan_loop(self):
        await self.client.wait_until_ready()

        self.stats_channel = await self.client.fetch_channel(STATS_CHANNEL_ID)

        while not self.client.is_closed():
            stats = Statistics()
            data = stats.get_dictionary()

            now = datetime.datetime.now()

            print(f"Container Scan Dated {now}", flush=True)
            save(data)

            # -----------------------------
            # Extract values
            # -----------------------------
            ram = data["ram"]["usage_percent"]
            cpu = data["cpu"]["usage_percent"]
            disk = data["disk"]["usage_percent"]

            # -----------------------------
            # Build stats message
            # -----------------------------
            message = self.format_stats(data)

            await self.stats_channel.send(message)

            # -----------------------------
            # Warning system
            # -----------------------------
            warnings = []

            # RAM
            if ram >= RAM_THRESHOLD:
                self.alert_counts["ram"] += 1
                if self.alert_counts["ram"] <= WARNING_REPEAT:
                    warnings.append(f"🚨 HIGH RAM USAGE: {ram}%")
            else:
                self.alert_counts["ram"] = 0

            # CPU
            if cpu >= CPU_THRESHOLD:
                self.alert_counts["cpu"] += 1
                if self.alert_counts["cpu"] <= WARNING_REPEAT:
                    warnings.append(f"🚨 HIGH CPU USAGE: {cpu}%")
            else:
                self.alert_counts["cpu"] = 0

            # DISK
            if disk >= DISK_THRESHOLD:
                self.alert_counts["disk"] += 1
                if self.alert_counts["disk"] <= WARNING_REPEAT:
                    warnings.append(f"🚨 HIGH DISK USAGE: {disk}%")
            else:
                self.alert_counts["disk"] = 0

            # Send warnings (if any)
            for w in warnings:
                await self.stats_channel.send(w)

            await asyncio.sleep(10)

    def format_stats(self, data):
        message = "📊 **Container Stats**\n\n"

        # RAM
        ram = data["ram"]
        message += "🧠 **RAM**\n"
        message += f"• Total: {ram['total_gb']} GB\n"
        message += f"• Used: {ram['used_gb']} GB\n"
        message += f"• Available: {ram['available_gb']} GB\n"
        message += f"• Usage: {ram['usage_percent']}%\n\n"

        # CPU
        cpu = data["cpu"]
        message += "⚙️ **CPU**\n"
        message += f"• Usage: {cpu['usage_percent']}%\n\n"

        # DISK
        disk = data["disk"]
        message += "💾 **Disk**\n"
        message += f"• Total: {disk['total_gb']} GB\n"
        message += f"• Used: {disk['used_gb']} GB\n"
        message += f"• Free: {disk['free_gb']} GB\n"
        message += f"• Usage: {disk['usage_percent']}%\n\n"

        # NETWORK
        net = data["network"]
        message += "🌐 **Network**\n"
        message += f"• Sent: {net['bytes_sent']} bytes\n"
        message += f"• Received: {net['bytes_received']} bytes\n"

        return message