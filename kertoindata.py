import json
import os

DATA_FILE = "kertoimet.json"

def lataa_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def tallenna_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def laske_muutos(alkuperainen, uusi):
    try:
        return round(((uusi - alkuperainen) / alkuperainen) * 100, 1)
    except ZeroDivisionError:
        return 0
