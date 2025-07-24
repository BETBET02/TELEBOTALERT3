import json
import os

KERTOIMET_TIEDOSTO = "kertoimet.json"

def lue_kertoimet():
    """Lue kertoimet JSON-tiedostosta. Palauttaa dictin."""
    if not os.path.exists(KERTOIMET_TIEDOSTO):
        return {}
    with open(KERTOIMET_TIEDOSTO, "r", encoding="utf-8") as f:
        return json.load(f)

def tallenna_kertoimet(kertoimet):
    """Tallenna kertoimet dict-muodossa JSON-tiedostoon."""
    with open(KERTOIMET_TIEDOSTO, "w", encoding="utf-8") as f:
        json.dump(kertoimet, f, ensure_ascii=False, indent=2)

def laske_fissio(vanha, uusi):
    """
    Laskee fissio-prosentin muutoksen kahden kertoimen välillä.
    Esim. jos vanha=2.00 ja uusi=2.40, fissio=20%
    """
    if vanha == 0:
        return 0
    fissio = ((uusi - vanha) / vanha) * 100
    return round(fissio, 2)
