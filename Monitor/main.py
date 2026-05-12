from classes import Statistics
from saving import save
import time
import datetime

def main():
    stats = Statistics()

    print(flush=True)

    print(f"Container Scan Dated {datetime.datetime.now()}", flush=True)
    
    print("History Succesfully Saved!", flush=True)
    
    save(stats.get_dictionary())


if __name__ == "__main__":
    while True:
        main()
        time.sleep(10)