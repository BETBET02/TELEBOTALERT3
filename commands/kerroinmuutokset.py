import requests
from telegram import Update
from telegram.ext import ContextTypes
from leagues import LEAGUES
from kertoimet import lue_kertoimet, tallenna_kertoimet, laske_fissio
from config import SPORTSRADAR_API_KEY, THRESHOLD_PERCENT

API_BASE = "https://api.sportsdata.io/v4/soccer"

def hae_ottelut(sarja_id):
    url = f"https://api.sportradar.com/soccer-tournament/v2/en/competitions/{sarja_id}/schedule.json?api_key={SPORTSRADAR_API_KEY}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    data = resp.json()
    return data.get("events", [])

async def kerroinmuutokset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Anna sarjan tai joukkueen nimi komennon jälkeen.")
        return

    hakusana = context.args[0]
    viesti = ""

    if hakusana in LEAGUES:
        sarja_id = LEAGUES[hakusana]
        ottelut = hae_ottelut(sarja_id)
        if not ottelut:
            await update.message.reply_text(f"Ei löytynyt otteluita sarjalle {hakusana}.")
            return

        kertoimet_data = lue_kertoimet()
        muutokset = []

        for ottelu in ottelut:
            event_id = ottelu["id"]

            # Tässä esimerkissä simuloidaan uudet kertoimet
            uusi_kertoimet = {
                "Unibet": {"match_winner_1": 2.4, "match_winner_2": 3.1},
                "Bet365": {"match_winner_1": 2.3, "match_winner_2": 3.2},
            }

            alku_kertoimet = kertoimet_data.get(event_id, {})
            for bookie, markets in uusi_kertoimet.items():
                for market, uusi_kerroin in markets.items():
                    alku_kerroin = alku_kertoimet.get(bookie, {}).get(market)
                    if alku_kerroin is None:
                        # Tallennetaan alkuperäinen kerroin
                        if event_id not in kertoimet_data:
                            kertoimet_data[event_id] = {}
                        if bookie not in kertoimet_data[event_id]:
                            kertoimet_data[event_id][bookie] = {}
                        kertoimet_data[event_id][bookie][market] = uusi_kerroin
                    else:
                        fissio = laske_fissio(alku_kerroin, uusi_kerroin)
                        if fissio >= THRESHOLD_PERCENT:
                            muutokset.append(f"{bookie} {market} fissio {fissio:.1f}% nousee {alku_kerroin} -> {uusi_kerroin}")

        tallenna_kertoimet(kertoimet_data)

        if muutokset:
            viesti = "\n".join(muutokset)
        else:
            viesti = f"Ei merkittäviä kerroinmuutoksia sarjassa {hakusana}."

        await update.message.reply_text(viesti)

    else:
        await update.message.reply_text(f"Sarjaa tai joukkuetta '{hakusana}' ei löydy. Käytä jotain seuraavista: {', '.join(LEAGUES.keys())}")
