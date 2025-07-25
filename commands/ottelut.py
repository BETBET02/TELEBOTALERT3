from telegram import Update
from telegram.ext import ContextTypes
from utils.api import fetch_json

# Esim. sarjan nimi "Brasil Serie A"
async def ottelut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Anna sarjan nimi komennon jälkeen, esim. /ottelut Brasil Serie A")
        return
    
    sarja_haku = " ".join(context.args).lower()

    # Haetaan sarjat
    data = await fetch_json("sports/sr:sport:1/competitions.json")
    competitions = data.get("competitions", [])

    # Etsitään kilpailu, joka vastaa käyttäjän hakua
    sarja = None
    for comp in competitions:
        if sarja_haku in comp.get("name", "").lower():
            sarja = comp
            break

    if not sarja:
        await update.message.reply_text(f"Sarjaa '{sarja_haku}' ei löytynyt.")
        return

    # Haetaan ottelut sarjassa
    season_id = sarja.get("id")  # esim. "sr:competition:1"
    # Käytetään season_idä endpointissa:
    endpoint = f"sport_events/{season_id}/sport_event_markets.json"
    
    try:
        ottelut_data = await fetch_json(endpoint)
    except Exception as e:
        await update.message.reply_text(f"Virhe haettaessa ottelutietoja: {e}")
        return

    # Rakennetaan viesti otteluista ja kertoimista
    viesti = f"Ottelut sarjassa {sarja.get('name')}:\n\n"

    events = ottelut_data.get("sport_event_markets", [])
    if not events:
        viesti += "Ei otteluita tällä hetkellä."
        await update.message.reply_text(viesti)
        return

    for event in events:
        # Ottelutiedot
        event_data = event.get("sport_event", {})
        home_team = event_data.get("competitors", [{}])[0].get("name", "Tuntematon")
        away_team = event_data.get("competitors", [{}])[1].get("name", "Tuntematon")
        start_time = event_data.get("scheduled", "tuntematon aika")

        # Kertoimet (esim. ensimmäinen markkina ja sen ensimmäinen kerroin)
        markets = event.get("markets", [])
        if markets and markets[0].get("outcomes"):
            outcomes = markets[0]["outcomes"]
            kertoimet_str = ", ".join(
                f"{o.get('name')}: {o.get('price')}" for o in outcomes
            )
        else:
            kertoimet_str = "Kertoimia ei saatavilla"

        viesti += f"{home_team} - {away_team} | Aloitus: {start_time}\nKertoimet: {kertoimet_str}\n\n"

    await update.message.reply_text(viesti)
