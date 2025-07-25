import requests
from telegram import Update
from telegram.ext import ContextTypes
from leagues import LEAGUES
from datetime import datetime
from config import SPORTSRADAR_API_KEY

DAILY_URL = "https://api.sportradar.com/soccer/trial/v4/en/schedules/{date}/schedules.json?api_key={key}"
PROBS_URL = "https://api.sportradar.com/soccer-probabilities/trial/v4/en/sport_events/upcoming_probabilities.json?api_key={key}"

async def ottelut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Anna liigan nimi ja päivämäärä, esim. `/ottelut seriea 26.07.2025`")
        return

    sarja = context.args[0].lower()
    comp_id = LEAGUES.get(sarja)
    if not comp_id:
        await update.message.reply_text(f"Sarjaa '{sarja}' ei tunnistettu.")
        return

    try:
        paiva = datetime.strptime(context.args[1], "%d.%m.%Y").strftime("%Y-%m-%d")
    except:
        await update.message.reply_text("Päivämäärä väärässä muodossa. Käytä DD.MM.YYYY")
        return

    resp = requests.get(DAILY_URL.format(date=paiva, key=SPORTSRADAR_API_KEY))
    if resp.status_code != 200:
        await update.message.reply_text(f"Virhe ottelulistassa: {resp.status_code}")
        return
    schedules = resp.json().get("schedules", [])

    resp2 = requests.get(PROBS_URL.format(key=SPORTSRADAR_API_KEY))
    if resp2.status_code != 200:
        await update.message.reply_text(f"Virhe kertoimissa: {resp2.status_code}")
        return
    probs = resp2.json().get("sport_event_upcoming_probabilities", [])

    # Kokoa ottelut liigan kilpailussa
    otteluet = []
    for s in schedules:
        evt = s.get("sport_event", {})
        ctx = evt.get("sport_event_context", {})
        if ctx.get("competition", {}).get("id") != comp_id:
            continue
        otteluet.append(evt)

    if not otteluet:
        await update.message.reply_text(f"Ei otteluita sarjassa {sarja} päivälle {paiva}.")
        return

    viesti = ""
    for ott in otteluet:
        ev_id = ott["id"]
        koti = ott["competitors"][0]["name"]
        vieras = ott["competitors"][1]["name"]
        aika = ott.get("start_time", ott.get("scheduled", ""))

        odds = {}
        for p in probs:
            if p.get("id") == ev_id:
                # p.probabilities sisältää odds
                for prob in p.get("probabilities", []):
                    odds.update({prob["name"]: prob["value"]})
                break

        kerrot = f"{odds.get('home_win','-')} / {odds.get('draw','-')} / {odds.get('away_win','-')}"
        viesti += f"\n{paiva} — {koti} vs {vieras} @ {aika}\nKertoimet: {kerrot}\n"

    await update.message.reply_text(viesti[:4096])
