import json
import datetime
import os

URL = "history/"


def save(data: dict):
    os.makedirs(URL, exist_ok=True)

    filepath = os.path.join(URL, "history.jsonl")

    entry = {
        "timestamp": int(datetime.datetime.now().timestamp()),
        "data": data
    }

    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")