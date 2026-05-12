import psutil

class Statistics:
    def __init__(self):
        mem = psutil.virtual_memory()
        
        self.total_ram = round(mem.total / (1024**3), 2)
        self.used_ram = round(mem.used / (1024**3), 2)
        self.available_ram = round(mem.available / (1024**3), 2)
        self.ram_usage = mem.percent

        self.cpu_usage = psutil.cpu_percent(interval=1)
        
        disk = psutil.disk_usage("/")
        
        self.total_disk = round(disk.total / (1024**3), 2)
        self.used_disk = round(disk.used / (1024**3), 2)
        self.free_disk = round(disk.free / (1024**3), 2)
        self.disk_usage = disk.percent
        
        net = psutil.net_io_counters()
        
        self.bytes_sent = net.bytes_sent
        self.bytes_received = net.bytes_recv
        
    def printMemory(self):
        print(f"{self.used_ram}gb/{self.total_ram}gb of RAM used ({self.ram_usage}%)")
        
    def printCpu(self):
        print(f"{self.cpu_usage}% of CPU used")
    def printDisk(self):
        print(f"{self.used_disk}gb/{self.total_disk}gb of DISK used ({self.disk_usage}%)")
        