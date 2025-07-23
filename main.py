import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
SPORTSRADAR_API_KEY = os.getenv("SPORTSRADAR_API_KEY")

LEAGUE_IDS = {
    "nhl": "fd560107-a85b-4388-ab0d-655ad022aff7",
    # Lisää muut liigat tähän tarvittaessa
}

async def loukkaantumiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or args[0].lower() not in LEAGUE_IDS:
        await update.message.reply_text(
            "Käytä komentoa muodossa:\n/loukkaantumiset <liiga>\n"
            "Esim.:\n/loukkaantumiset nhl"
        )
        return

    league_key = args[0].lower()
    league_id = LEAGUE_IDS[league_key]

    url = f"https://api.sportsdata.io/v3/nhl/injuries/json/InjuriesByLeague/{league_id}"
    headers = {
        "Ocp-Apim-Subscription-Key": SPORTSRADAR_API_KEY
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        await update.message.reply_text("Virhe haettaessa loukkaantumistietoja.")
        return

    data = response.json()

    teams = data.get("teams", [])
    if not teams:
        await update.message.reply_text("Ei löydetty loukkaantumistietoja.")
        return

    reply_text = f"<b>Loukkaantumistiedot: {league_key.upper()}</b>\n\n"

    for team in teams:
        team_name = team.get("name", "Tuntematon joukkue")
        players = team.get("players", [])
        if not players:
            continue
        reply_text += f"🏒 <b>{team_name}</b>\n"
        for player in players:
            injuries = player.get("injuries", [])
            if not injuries:
                continue
            player_name = player.get("full_name", "Tuntematon pelaaja")
            for injury in injuries:
                desc = injury.get("desc", "Ei tietoa")
                status = injury.get("status", "Ei tietoa")
                start_date = injury.get("start_date", "Ei tietoa")
                comment = injury.get("comment", "")
                reply_text += f"• {player_name} - {desc} ({status}), alkaen {start_date}\n"
                if comment:
                    reply_text += f"  ▸ {comment}\n"
        reply_text += "\n"

    # Telegram-viestiraja noin 4096 merkkiä, tässä varmistetaan ettei ylitetä
    if len(reply_text) > 4000:
        reply_text = reply_text[:4000] + "\n\n[Viesti katkaistu]"

    await update.message.reply_text(reply_text, parse_mode="HTML", disable_web_page_preview=True)


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("loukkaantumiset", loukkaantumiset))
    print("Botti käynnissä...")
    app.run_polling()
