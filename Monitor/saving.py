import json
import datetime
import os

URL = "history/"


def save(data: dict):
    os.makedirs(URL, exist_ok=True)

    filepath = os.path.join(URL, "history.jsonl")

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "data": data
    }

    with open(filepath, "a") as f:
        f.write(json.dumps(entry, indent=1) + "\n")