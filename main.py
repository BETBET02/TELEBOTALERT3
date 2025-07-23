import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
SPORTSRADAR_API_KEY = os.getenv("SPORTSRADAR_API_KEY")

SEASONS = {
    "preseason": "4383ec83-6112-47f0-867a-8839145e1d58",
    "regular": "4a67cca6-b450-45f9-91c6-48e92ac19069",
    "postseason": "3c1bb21f-6523-4115-87ee-c8c16ed80421"
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

    url = f"https://api.sportradar.com/nhl/trial/v7/en/seasons/{season_id}/injuries.json"
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

    if len(reply_text) > 4000:
        reply_text = reply_text[:4000] + "\n\n[Viesti katkaistu]"

    await update.message.reply_text(reply_text, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("loukkaantumiset", loukkaantumiset))
    print("Botti käynnissä...")
    app.run_polling()
