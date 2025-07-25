import httpx
import os

API_KEY = os.getenv("SPORTRADAR_API_KEY")
BASE_URL = "https://api.sportradar.com/oddscomparison-prematch/trial/v2/en"

headers = {
    "accept": "application/json",
    "x-api-key": API_KEY
}

async def fetch_json(endpoint: str):
    url = f"{BASE_URL}/{endpoint}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
