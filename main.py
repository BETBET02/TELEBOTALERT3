import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Hae token ja API-avain ympäristömuuttujista
TOKEN = os.getenv("BOT_TOKEN")
SPORTSRADAR_API_KEY = os.getenv("SPORTSRADAR_API_KEY")

# NHL kausi (season ID)
SEASON_ID = "4a67cca6-b450-45f9-91c6-48e92ac19069"

async def loukkaantumiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://api.sportradar.com/nhl/trial/v7/en/seasons/{SEASON_ID}/injuries.json?api_key={SPORTSRADAR_API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        await update.message.reply_text(f"Virhe haettaessa loukkaantumistietoja: {response.status_code}")
        return

    data = response.json()

    # Data voi olla rakenne, jossa on joukkueita ja pelaajia loukkaantuneina
    # Esim: data["teams"] tai suoraan lista loukkaantumisista
    # Käydään läpi data ja kerätään viesti

    reply_text = "<b>NHL Loukkaantumistiedot</b>\n\n"

    teams = data.get("teams", [])
    if not teams:
        await update.message.reply_text("Ei löytynyt loukkaantumistietoja tällä kaudella.")
        return

    for team in teams:
        team_name = team.get("name", "Tuntematon joukkue")
        players = team.get("players", [])
        if not players:
            continue

        reply_text += f"🏒 <b>{team_name}</b>\n"
        for player in players:
            player_name = player.get("full_name", "Tuntematon pelaaja")
            injuries = player.get("injuries", [])
            if not injuries:
                continue
            for injury in injuries:
                desc = injury.get("desc", "Ei tietoa")
                status = injury.get("status", "Ei tietoa")
                start_date = injury.get("start_date", "Ei tiedossa")
                comment = injury.get("comment", "")
                reply_text += f"• {player_name} - {desc} ({status}), alkaen {start_date}\n"
                if comment:
                    reply_text += f"  ▸ {comment}\n"
        reply_text += "\n"

    # Rajoita viestin pituus (Telegramin max ~4096 merkkiä)
    if len(reply_text) > 4000:
        reply_text = reply_text[:4000] + "\n\n[Viesti katkaistu]"

    await update.message.reply_text(reply_text, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("loukkaantumiset", loukkaantumiset))
    print("Botti käynnissä...")
    app.run_polling()
