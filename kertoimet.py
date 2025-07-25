import json
import os

KERTOIMET_TIEDOSTO = "data/kertoimet.json"

def lue_kertoimet():
    if os.path.exists(KERTOIMET_TIEDOSTO):
        with open(KERTOIMET_TIEDOSTO, "r") as f:
            return json.load(f)
    return {}

def tallenna_kertoimet(data):
    with open(KERTOIMET_TIEDOSTO, "w") as f:
        json.dump(data, f, indent=2)

def laske_fissio(alku, uusi):
    try:
        muutos = abs(uusi - alku)
        return (muutos / alku) * 100
    except ZeroDivisionError:
        return 0
