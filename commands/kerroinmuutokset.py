import requests
from telegram import Update
from telegram.ext import ContextTypes
from leagues import LEAGUES
from kertoimet import lue_kertoimet, tallenna_kertoimet, laske_fissio
from config import SPORTSRADAR_API_KEY, THRESHOLD_PERCENT
from datetime import datetime, timezone

API_BASE = "https://api.sportradar.com/soccer/v4/en"

def hae_ottelut(season_id):
    url = f"{API_BASE}/seasons/{season_id}/schedules.json?api_key={SPORTSRADAR_API_KEY}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return []

    data = resp.json()
    kaikki_ottelut = data.get("sport_events", [])

    nyt = datetime.now(timezone.utc)
    tulevat_ottelut = [
        ottelu for ottelu in kaikki_ottelut
        if datetime.fromisoformat(ottelu["scheduled"].replace("Z", "+00:00")) > nyt
    ]

    return tulevat_ottelut

async def kerroinmuutokset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Anna sarjan nimi (esim. brasilia, valioliiga).")
        return

    hakusana = context.args[0].lower()
    season_id = LEAGUES.get(hakusana)

    if not season_id:
        await update.message.reply_text(f"Sarjaa {hakusana} ei tunnistettu.")
        return

    ottelut = hae_ottelut(season_id)

    if not ottelut:
        await update.message.reply_text(f"Ei löytynyt tulevia otteluita sarjalle {hakusana}.")
        return

    kertoimet_data = lue_kertoimet()
    muutokset = []

    for ottelu in ottelut:
        event_id = ottelu["id"]

        # Simuloidut kertoimet (korvaa oikealla kutsulla kun valmis)
        uusi_kertoimet = {
            "Unibet": {"match_winner_1": 2.4, "match_winner_2": 3.1},
            "Bet365": {"match_winner_1": 2.3, "match_winner_2": 3.2},
        }

        alku_kertoimet = kertoimet_data.get(event_id, {})
        for bookie, markets in uusi_kertoimet.items():
            for market, uusi_kerroin in markets.items():
                alku_kerroin = alku_kertoimet.get(bookie, {}).get(market)
                if alku_kerroin is None:
                    kertoimet_data.setdefault(event_id, {}).setdefault(bookie, {})[market] = uusi_kerroin
                else:
                    fissio = laske_fissio(alku_kerroin, uusi_kerroin)
                    if fissio >= THRESHOLD_PERCENT:
                        muutokset.append(
                            f"{bookie} {market} fissio {fissio:.1f}% nousee {alku_kerroin} -> {uusi_kerroin}"
                        )

    tallenna_kertoimet(kertoimet_data)

    if muutokset:
        await update.message.reply_text("\n".join(muutokset))
    else:
        await update.message.reply_text(f"Ei merkittäviä kerroinmuutoksia sarjassa {hakusana}.")
