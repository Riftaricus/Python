import asyncio
import datetime
import json
import os
import matplotlib.pyplot as plt

from classes import Statistics
from saving import save

STATS_CHANNEL_ID = 1503834424788389918

RAM_THRESHOLD = 80
CPU_THRESHOLD = 80
DISK_THRESHOLD = 85

WARNING_REPEAT = 3

HISTORY_FILE = "history/history.jsonl"


class Bot:
    def __init__(self, client):
        self.client = client
        self.stats_channel = None

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

            # -------------------------
            # Send normal stats
            # -------------------------
            await self.stats_channel.send(self.format_stats(data))

            # -------------------------
            # Alerts
            # -------------------------
            await self.handle_alerts(data)

            # -------------------------
            # Graph (every ~1 minute)
            # -------------------------
            if self.should_send_graph():
                path = self.generate_graph()

                await self.stats_channel.send(
                    content="📊 Resource Usage Graph",
                    file=__import__("discord").File(path)
                )

            await asyncio.sleep(10)

    # -------------------------
    # ALERT SYSTEM
    # -------------------------
    async def handle_alerts(self, data):
        ram = data["ram"]["usage_percent"]
        cpu = data["cpu"]["usage_percent"]
        disk = data["disk"]["usage_percent"]

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

        for w in warnings:
            await self.stats_channel.send(w)

    # -------------------------
    # FORMAT MESSAGE
    # -------------------------
    def format_stats(self, data):
        return (
            "📊 **Container Stats**\n\n"
            "🧠 RAM: {ram}%\n"
            "⚙️ CPU: {cpu}%\n"
            "💾 Disk: {disk}%\n"
            "🌐 Network: Sent {sent}, Received {recv}"
        ).format(
            ram=data["ram"]["usage_percent"],
            cpu=data["cpu"]["usage_percent"],
            disk=data["disk"]["usage_percent"],
            sent=data["network"]["bytes_sent"],
            recv=data["network"]["bytes_received"]
        )

    # -------------------------
    # GRAPH CONTROL
    # -------------------------
    def should_send_graph(self):
        # simple rule: every ~6 cycles (≈1 min)
        if not hasattr(self, "_cycle"):
            self._cycle = 0

        self._cycle += 1
        return self._cycle % 6 == 0

    # -------------------------
    # GRAPH GENERATION
    # -------------------------
    def generate_graph(self):
        times = []
        cpu = []
        ram = []
        disk = []

        if not os.path.exists(HISTORY_FILE):
            return None

        with open(HISTORY_FILE, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    data = entry["data"]

                    times.append(entry["timestamp"])
                    cpu.append(data["cpu"]["usage_percent"])
                    ram.append(data["ram"]["usage_percent"])
                    disk.append(data["disk"]["usage_percent"])

                except Exception:
                    continue

        plt.figure(figsize=(10, 5))

        plt.plot(times, cpu, label="CPU %")
        plt.plot(times, ram, label="RAM %")
        plt.plot(times, disk, label="Disk %")

        plt.xticks(rotation=45)
        plt.xlabel("Time")
        plt.ylabel("Usage %")
        plt.title("Container Resource Usage History")
        plt.legend()

        plt.tight_layout()

        path = "graph.png"
        plt.savefig(path)
        plt.close()

        return path