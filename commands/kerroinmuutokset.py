import requests
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config import SPORTSRADAR_API_KEY, THRESHOLD_PERCENT
from leagues import LEAGUES
from kertoimet import lue_kertoimet, tallenna_kertoimet, laske_fissio

API_URL = "https://api.sportradar.com/soccer/v4/en/schedules/{date}/summaries.json?api_key={key}"

def hae_paivan_ottelut_ja_kertoimet(pvm_str: str):
    url = API_URL.format(date=pvm_str, key=SPORTSRADAR_API_KEY)
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    return resp.json().get("summaries", [])

async def kerroinmuutokset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Anna sarjan nimi komennon jälkeen.")
        return

    hakusana = context.args[0].lower()
    competition_id = LEAGUES.get(hakusana)
    if not competition_id:
        await update.message.reply_text(f"Sarjaa {hakusana} ei löydy.")
        return

    pvm = datetime.utcnow().strftime("%Y-%m-%d")
    ottelut = hae_paivan_ottelut_ja_kertoimet(pvm)
    kertoimet_data = lue_kertoimet()

    muutokset = []

    for ottelu in ottelut:
        comp_id = ottelu.get("sport_event", {}).get("tournament", {}).get("id")
        if comp_id != competition_id:
            continue

        event_id = ottelu.get("sport_event", {}).get("id")
        koti = ottelu["sport_event"]["competitors"][0]["name"]
        vieras = ottelu["sport_event"]["competitors"][1]["name"]
        markets = ottelu.get("markets", [])

        for market in markets:
            market_name = market.get("name")
            for bookmaker in market.get("bookmakers", []):
                bookie = bookmaker.get("name")
                for outcome in bookmaker.get("outcomes", []):
                    outcome_name = outcome["name"]
                    uusi_kerroin = outcome["odds"]

                    alku_kerroin = (
                        kertoimet_data
                        .get(event_id, {})
                        .get(bookie, {})
                        .get(f"{market_name}:{outcome_name}")
                    )

                    if alku_kerroin is None:
                        # Tallennetaan uusi kerroin
                        kertoimet_data.setdefault(event_id, {}).setdefault(bookie, {})[f"{market_name}:{outcome_name}"] = uusi_kerroin
                    else:
                        fissio = laske_fissio(alku_kerroin, uusi_kerroin)
                        if fissio >= THRESHOLD_PERCENT:
                            muutokset.append(
                                f"{koti} - {vieras}\n{bookie} {market_name} {outcome_name}: "
                                f"{alku_kerroin} → {uusi_kerroin} ({fissio:.1f}%)"
                            )

    tallenna_kertoimet(kertoimet_data)

    if muutokset:
        viesti = "\n\n".join(muutokset)
    else:
        viesti = f"Ei merkittäviä kerroinmuutoksia sarjassa {hakusana}."

    await update.message.reply_text(viesti[:4096])
