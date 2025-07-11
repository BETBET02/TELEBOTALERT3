import os
import aiohttp

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# Lista sarjoista esim. jalkapallo, jääkiekko yms. — voit muokata
FOOTBALL_LEAGUES = ["laliga", "bundesliga", "serie-a", "ligue-1", "premier-league", "eredivisie", "serie-a-brasil", "liga-professional"]
HOCKEY_LEAGUES = ["nhl", "shl", "nla", "smliga", "del", "liiga"]
TENNIS_SERIES = ["atp", "challenger"]
OTHER_SPORTS = ["mlb", "nba"]

async def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?category=sports&apiKey={NEWS_API_KEY}&language=en"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data["articles"]
            else:
                print(f"NewsAPI error: {resp.status}")
                return []

async def fetch_odds_changes():
    # OddsAPI esimerkki - korvaa endpoint oikealla ja lisää parametrit
    url = f"https://api.the-odds-api.com/v4/sports/odds/?apiKey={ODDS_API_KEY}&regions=eu&markets=h2h"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            else:
                print(f"OddsAPI error: {resp.status}")
                return []

async def fetch_sports_news():
    # Tässä voi yhdistää eri lähteitä tai suodattaa artikkeleita tärkeyden mukaan
    return await fetch_news()

async def fetch_lineup_changes():
    # Jos sinulla on API, josta saat kokoonpanomuutokset, toteuta tähän
    # Toistaiseksi tyhjä lista
    return []

async def fetch_props_alerts():
    # Toteuta tämä kun sinulla on data props-vedoista
    return []
