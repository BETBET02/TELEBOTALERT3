import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Haetaan tokenit ympäristömuuttujista
TOKEN = os.getenv("BOT_TOKEN")
SPORTSRADAR_API_KEY = os.getenv("SPORTSRADAR_API_KEY")

# Liigan ja kausien ID:t (voit lisätä tarvittaessa)
LEAGUE_ID = "fd560107-a85b-4388-ab0d-655ad022aff7"

SEASONS = {
    "preseason": "4383ec83-6112-47f0-867a-8839145e1d58",
    "regular": "4a67cca6-b450-45f9-91c6-48e92ac19069",
    "postseason": "3c1bb21f-6523-4115-87ee-c8c16ed80421"
}

# Joukkueiden id:t, voit lisätä tai muokata
TEAM_IDS = {
    "Avalanche": "4415ce44-0f24-11e2-8525-18a905767e44",
    "Blackhawks": "4416272f-0f24-11e2-8525-18a905767e44",
    "Blue Jackets": "44167db4-0f24-11e2-8525-18a905767e44",
    "Blues": "441660ea-0f24-11e2-8525-18a905767e44",
    "Bruins": "4416ba1a-0f24-11e2-8525-18a905767e44",
    "Canada": "2daa7c51-22ba-41ba-97bd-a920782b8541",
    "Canadiens": "441713b7-0f24-11e2-8525-18a905767e44",
    "Canucks": "4415b0a7-0f24-11e2-8525-18a905767e44",
    "Capitals": "4417eede-0f24-11e2-8525-18a905767e44",
    "Devils": "44174b0c-0f24-11e2-8525-18a905767e44",
    "Ducks": "441862de-0f24-11e2-8525-18a905767e44",
    "Flames": "44159241-0f24-11e2-8525-18a905767e44",
    "Flyers": "44179d47-0f24-11e2-8525-18a905767e44",
    "Golden Knights": "42376e1c-6da8-461e-9443-cfcf0a9fcc4d",
    "Hurricanes": "44182a9d-0f24-11e2-8525-18a905767e44",
    "Islanders": "441766b9-0f24-11e2-8525-18a905767e44",
    "Jets": "44180e55-0f24-11e2-8525-18a905767e44",
    "Kings": "44151f7a-0f24-11e2-8525-18a905767e44",
    "Kraken": "1fb48e65-9688-4084-8868-02173525c3e1",
    "Lightning": "4417d3cb-0f24-11e2-8525-18a905767e44",
    "Mammoth": "715a1dba-4e9f-4158-8346-3473b6e3557f",
    "Maple Leafs": "441730a9-0f24-11e2-8525-18a905767e44",
    "Oilers": "4415ea6c-0f24-11e2-8525-18a905767e44",
    "Panthers": "4418464d-0f24-11e2-8525-18a905767e44",
    "Penguins": "4417b7d7-0f24-11e2-8525-18a905767e44",
    "Predators": "441643b7-0f24-11e2-8525-18a905767e44",
    "Rangers": "441781b9-0f24-11e2-8525-18a905767e44",
    "Red Wings": "44169bb9-0f24-11e2-8525-18a905767e44",
    "Sabres": "4416d559-0f24-11e2-8525-18a905767e44",
    "Senators": "4416f5e2-0f24-11e2-8525-18a905767e44",
    "Sharks": "44155909-0f24-11e2-8525-18a905767e44",
    "Stars": "44157522-0f24-11e2-8525-18a905767e44",
    "Wild": "4416091c-0f24-11e2-8525-18a905767e44",
}

async def loukkaantumiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 1:
        await update.message.reply_text(
            "Käytä komentoa muodossa:\n/loukkaantumiset <kausi>\n"
            "Kausivaihtoehdot: preseason, regular, postseason\n"
            "Esim.:\n/loukkaantumiset regular"
        )
        return

    season_key = args[0].lower()
    if season_key not in SEASONS:
        await update.message.reply_text(
            f"Virheellinen kausi! Valitse: preseason, regular, postseason"
        )
        return

    season_id = SEASONS[season_key]

    url = f"https://api.sportradar.com/nhl/trial/v7/en/league/{season_id}/injuries.json"
    headers = {
        "accept": "application/json",
        "x-api-key": SPORTSRADAR_API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        await update.message.reply_text(f"Virhe haettaessa loukkaantumistietoja (status code {response.status_code}).")
        return

    data = response.json()
    if "teams" not in data:
        await update.message.reply_text("Loukkaantumistietoja ei löytynyt.")
        return

    reply_text = f"<b>Loukkaantumistiedot - {season_key.capitalize()} Season</b>\n\n"
    for team in data["teams"]:
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
                start_date = injury.get("start_date", "Ei tietoa")
                comment = injury.get("comment", "")
                reply_text += f"• {player_name} - {desc} ({status}), alkaen {start_date}\n"
                if comment:
                    reply_text += f"  ▸ {comment}\n"
        reply_text += "\n"

    # Varmistetaan ettei viesti ole liian pitkä Telegramissa (~4096 merkkiä max)
    if len(reply_text) > 4000:
        reply_text = reply_text[:4000] + "\n\n[Viesti katkaistu]"

    await update.message.reply_text(reply_text, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("loukkaantumiset", loukkaantumiset))
    print("Botti käynnissä...")
    app.run_polling()
