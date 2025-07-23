import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = os.getenv("SPORTSRADAR_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Tässä esimerkkinä joitain liigoja ja niiden Sportsradarin league ID:t (placeholder)
LEAGUES = {
    "nhl": {
        "name": "NHL",
        "league_id": "sr:league:51",
        "base_url": "https://api.sportradar.com/nhl/trial/v7/en"
    },
    "nba": {
        "name": "NBA",
        "league_id": "sr:league:46",
        "base_url": "https://api.sportradar.com/nba/trial/v7/en"
    },
    "la_liga": {
        "name": "La Liga",
        "league_id": "sr:competition:17",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "bundesliga": {
        "name": "Bundesliga",
        "league_id": "sr:competition:10",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "serie_a_italia": {
        "name": "Serie A Italia",
        "league_id": "sr:competition:11",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "serie_a_brasilia": {
        "name": "Serie A Brasilia",
        "league_id": "sr:competition:44",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "liga_professional": {
        "name": "Liga Profesional Argentina",
        "league_id": "sr:competition:57",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "ligue_1": {
        "name": "Ligue 1",
        "league_id": "sr:competition:13",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "eredivisie": {
        "name": "Eredivisie",
        "league_id": "sr:competition:19",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "valioliiga": {
        "name": "Valioliiga",
        "league_id": "sr:competition:8",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "veikkausliiga": {
        "name": "Veikkausliiga",
        "league_id": "sr:competition:131",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "allsvenskan": {
        "name": "Allsvenskan",
        "league_id": "sr:competition:124",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "eliteserien": {
        "name": "Eliteserien",
        "league_id": "sr:competition:134",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "turkin_super_lig": {
        "name": "Turkin Super Lig",
        "league_id": "sr:competition:102",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "tanskan_super_lig": {
        "name": "Tanskan Super Lig",
        "league_id": "sr:competition:127",
        "base_url": "https://api.sportradar.com/soccer/trial/v4/en"
    },
    "khl": {
        "name": "KHL",
        "league_id": "sr:league:77",
        "base_url": "https://api.sportradar.com/hockey/ru/trial/v7/en"
    },
    "shl": {
        "name": "SHL",
        "league_id": "sr:league:53",
        "base_url": "https://api.sportradar.com/hockey/se/trial/v7/en"
    },
    "liiga": {
        "name": "Liiga",
        "league_id": "sr:league:54",
        "base_url": "https://api.sportradar.com/hockey/fi/trial/v7/en"
    },
    "extra_liga": {
        "name": "Extra Liga (Tsekki)",
        "league_id": "sr:league:39",
        "base_url": "https://api.sportradar.com/hockey/ru/trial/v7/en"
    },
    "nla": {
        "name": "NLA (Sveitsi)",
        "league_id": "sr:league:55",
        "base_url": "https://api.sportradar.com/hockey/ch/trial/v7/en"
    },
}

def get_teams(league):
    """Hakee joukkueet annetusta liigasta."""
    base_url = league["base_url"]
    league_id = league["league_id"]
    url = f"{base_url}/seasons/{league_id}/teams.json?api_key={API_KEY}"

    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        # Olettaen että joukkueet löytyvät data["teams"] tai vastaava
        teams = data.get("teams") or data.get("competitors") or []
        return teams
    except Exception as e:
        print(f"Virhe joukkueiden haussa {league['name']}: {e}")
        return []

def get_injuries_for_team(base_url, team_id):
    """Hakee loukkaantumistiedot joukkueelle."""
    url = f"{base_url}/teams/{team_id}/injuries.json?api_key={API_KEY}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        injuries = data.get("injuries", [])
        return injuries
    except Exception as e:
        print(f"Virhe loukkaantumistiedoissa joukkueelle {team_id}: {e}")
        return []

async def loukkaantumiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    search_term = args[0].lower() if args else None

    msg = ""

    # Suorita joko haku kaikista liigoista tai haetaan yksi liiga/joukkue
    if not search_term:
        # Kaikki liigat
        for key, league in LEAGUES.items():
            msg += f"\n🏟️ *{league['name']}*:\n"
            teams = get_teams(league)
            if not teams:
                msg += "Ei joukkueita saatavilla.\n"
                continue

            for team in teams:
                team_id = team.get("id") or team.get("sr_id") or team.get("team_id") or team.get("reference")
                team_name = team.get("name") or team.get("market") or "Joukkue"
                injuries = get_injuries_for_team(league["base_url"], team_id)
                if injuries:
                    for injury in injuries:
                        player = injury.get("player") or {}
                        player_name = player.get("name") or "Pelaaja"
                        injury_desc = injury.get("description") or "Loukkaantuminen"
                        msg += f"• {player_name} ({team_name}): {injury_desc}\n"
                else:
                    msg += f"• Ei loukkaantumisia joukkueella {team_name}\n"
    else:
        # Haetaan annetun liigan tai joukkueen loukkaantumiset
        found_league = None
        for key, league in LEAGUES.items():
            if search_term in [key, league["name"].lower()]:
                found_league = league
                break

        if found_league:
            msg += f"\n🏟️ *{found_league['name']}*:\n"
            teams = get_teams(found_league)
            if not teams:
                msg += "Ei joukkueita saatavilla.\n"
            else:
                for team in teams:
                    team_id = team.get("id") or team.get("sr_id") or team.get("team_id") or team.get("reference")
                    team_name = team.get("name") or team.get("market") or "Joukkue"
                    injuries = get_injuries_for_team(found_league["base_url"], team_id)
                    if injuries:
                        for injury in injuries:
                            player = injury.get("player") or {}
                            player_name = player.get("name") or "Pelaaja"
                            injury_desc = injury.get("description") or "Loukkaantuminen"
                            msg += f"• {player_name} ({team_name}): {injury_desc}\n"
                    else:
                        msg += f"• Ei loukkaantumisia joukkueella {team_name}\n"
        else:
            # Jos ei löytynyt liigaa, yritetään etsiä joukkue nimellä (yksinkertaistettuna)
            msg += "Annetulla nimellä ei löytynyt liigaa. Yritä uudelleen."

    if not msg.strip():
        msg = "Ei loukkaantumistietoja saatavilla."

    await update.message.reply_text(msg)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("loukkaantumiset", loukkaantumiset))
    print("Botti käynnissä...")
    app.run_polling()
