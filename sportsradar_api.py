import os
import requests

API_KEY = os.getenv("SPORTSRADAR_API_KEY")  # Tai korvaa omalla avaimellasi
SEASON_ID = "4a67cca6-b450-45f9-91c6-48e92ac19069"  # NHL kausi-id

team_ids = [
    "4415ce44-0f24-11e2-8525-18a905767e44",  # Avalanche
    "4416272f-0f24-11e2-8525-18a905767e44",  # Blackhawks
    "44167db4-0f24-11e2-8525-18a905767e44",  # Blue Jackets
    "441660ea-0f24-11e2-8525-18a905767e44",  # Blues
    "4416ba1a-0f24-11e2-8525-18a905767e44",  # Bruins
    "2daa7c51-22ba-41ba-97bd-a920782b8541",  # Canada (team)
    "441713b7-0f24-11e2-8525-18a905767e44",  # Canadiens
    "4415b0a7-0f24-11e2-8525-18a905767e44",  # Canucks
    "4417eede-0f24-11e2-8525-18a905767e44",  # Capitals
    "44174b0c-0f24-11e2-8525-18a905767e44",  # Devils
    "441862de-0f24-11e2-8525-18a905767e44",  # Ducks
    "7773b2a8-5a35-409a-b109-01ded63e0775",  # EHC Red Bull Munchen (ei NHL)
    "535534b6-78cf-4650-824c-fb9a15be5988",  # Eisbaren Berlin (ei NHL)
    "8ca3ad35-b16c-47cd-a3f5-678fc45718f1",  # Finland (team)
    "44159241-0f24-11e2-8525-18a905767e44",  # Flames
    "44179d47-0f24-11e2-8525-18a905767e44",  # Flyers
    "42376e1c-6da8-461e-9443-cfcf0a9fcc4d",  # Golden Knights (Vegas)
    "468e2568-b105-4472-9c6c-bf53d9cf2e19",  # Hughes (team)
    "44182a9d-0f24-11e2-8525-18a905767e44",  # Hurricanes
    "441766b9-0f24-11e2-8525-18a905767e44",  # Islanders
    "44180e55-0f24-11e2-8525-18a905767e44",  # Jets
    "44151f7a-0f24-11e2-8525-18a905767e44",  # Kings
    "1fb48e65-9688-4084-8868-02173525c3e1",  # Kraken (Seattle)
    "4417d3cb-0f24-11e2-8525-18a905767e44",  # Lightning
    "2bac13fb-85e2-4901-adbc-dab87365e6c9",  # MacKinnon (team)
    "715a1dba-4e9f-4158-8346-3473b6e3557f",  # Mammoth (Utah)
    "441730a9-0f24-11e2-8525-18a905767e44",  # Maple Leafs
    "b7c79007-995e-4961-8a02-0c6f9dd65269",  # Matthews (team)
    "67be4fe9-b990-4f1a-83ff-82c9a62f71b8",  # McDavid (team)
    "4415ea6c-0f24-11e2-8525-18a905767e44",  # Oilers
    "4418464d-0f24-11e2-8525-18a905767e44",  # Panthers (Florida)
    "4417b7d7-0f24-11e2-8525-18a905767e44",  # Penguins
    "441643b7-0f24-11e2-8525-18a905767e44",  # Predators
    "441781b9-0f24-11e2-8525-18a905767e44",  # Rangers
    "44169bb9-0f24-11e2-8525-18a905767e44",  # Red Wings
    "9aa0e461-0d27-4a08-a9f5-5cdea0acd772",  # SC Bern (ei NHL)
    "4416d559-0f24-11e2-8525-18a905767e44",  # Sabres
    "4416f5e2-0f24-11e2-8525-18a905767e44",  # Senators
    "44155909-0f24-11e2-8525-18a905767e44",  # Sharks
    "44157522-0f24-11e2-8525-18a905767e44",  # Stars
    "23ba9bca-71b5-4ce0-ace4-d2ef1cea9607",  # Sweden (team)
    "062d9e85-6d5b-463b-91c6-2d1cd044a6cf",  # TBD (team)
    "31a76837-ac41-4af0-ae6a-5d058b7e5626",  # USA (team)
    "4416091c-0f24-11e2-8525-18a905767e44",  # Wild
]

def fetch_team_profile(team_id):
    url = BASE_URL.format(team_id=team_id)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        print(f"Team: {data.get('name', 'N/A')}, Market: {data.get('market', 'N/A')}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error for team {team_id}: {http_err}")
    except Exception as err:
        print(f"Error for team {team_id}: {err}")

for team_id in team_ids:
    fetch_team_profile(team_id)
