import os
import requests
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

SPORTSRADAR_API_KEY = os.getenv("SPORTSRADAR_API_KEY")
TOKEN = os.getenv("BOT_TOKEN")

# Funktiot SportRadar API-kutsuihin
def get_player_transfers():
    url = f"https://api.sportradar.com/nhl/trial/v7/en/player_transfers.json?api_key={SPORTSRADAR_API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

def get_injuries():
    url = f"https://api.sportradar.com/nhl/trial/v7/en/injuries.json?api_key={SPORTSRADAR_API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

def get_lineups():
    # Esimerkki: haetaan viimeisimmän päivän kokoonpanot
    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://api.sportradar.com/nhl/trial/v7/en/games/{today}/lineups.json?api_key={SPORTSRADAR_API_KEY}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return None

# Telegram-komento
async def uutiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text(
            "Käytä komentoa muodossa:\n"
            "/uutiset <aihe>\n"
            "Esim:\n"
            "/uutiset siirrot\n"
            "/uutiset loukkaantumiset\n"
            "/uutiset kokoonpanot"
        )
        return

    aihe = args[0].lower()

    if aihe == "siirrot":
        data = get_player_transfers()
        if not data:
            await update.message.reply_text("Ei löytynyt siirtotietoja.")
            return
        viesti = "Pelaajasiirrot:\n"
        transfers = data.get("transfers", [])
        if not transfers:
            viesti += "Ei siirtoja tällä hetkellä."
        else:
            for t in transfers[:10]:  # max 10
                player = t.get("player", {}).get("name", "Tuntematon")
                from_team = t.get("from_team", {}).get("name", "Tuntematon")
                to_team = t.get("to_team", {}).get("name", "Tuntematon")
                date = t.get("transfer_date", "Tuntematon päivämäärä")
                viesti += f"• {player}: {from_team} → {to_team} ({date})\n"
        await update.message.reply_text(viesti)

    elif aihe == "loukkaantumiset":
        data = get_injuries()
        if not data:
            await update.message.reply_text("Ei löytynyt loukkaantumistietoja.")
            return
        viesti = "Loukkaantumiset:\n"
        injuries = data.get("injuries", [])
        if not injuries:
            viesti += "Ei loukkaantumistietoja tällä hetkellä."
        else:
            for i in injuries[:10]:
                player = i.get("player", {}).get("name", "Tuntematon")
                injury_desc = i.get("injury", "Tuntematon vamma")
                status = i.get("status", "Tuntematon status")
                viesti += f"• {player}: {injury_desc} ({status})\n"
        await update.message.reply_text(viesti)

    elif aihe == "kokoonpanot":
        data = get_lineups()
        if not data:
            await update.message.reply_text("Ei löytynyt kokoonpanotietoja.")
            return
        viesti = "Kokoonpanot:\n"
        games = data.get("games", [])
        if not games:
            viesti += "Ei kokoonpanoja tänään."
        else:
            for game in games[:5]:  # max 5 ottelua
                home = game.get("home", {}).get("name", "Tuntematon")
                away = game.get("away", {}).get("name", "Tuntematon")
                viesti += f"• {home} vs {away}\n"
                lineup_home = game.get("lineups", {}).get("home", [])
                lineup_away = game.get("lineups", {}).get("away", [])
                viesti += "  Kotijoukkue:\n"
                for player in lineup_home[:5]:  # max 5 pelaajaa
                    viesti += f"   - {player.get('name', 'Tuntematon')}\n"
                viesti += "  Vierasjoukkue:\n"
                for player in lineup_away[:5]:
                    viesti += f"   - {player.get('name', 'Tuntematon')}\n"
        await update.message.reply_text(viesti)

    else:
        await update.message.reply_text("Tuntematon aihe. Käytä: siirrot, loukkaantumiset tai kokoonpanot.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("uutiset", uutiset))
    print("Botti käynnissä...")
    app.run_polling()
