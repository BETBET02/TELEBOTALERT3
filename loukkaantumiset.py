import requests

API_KEY = "1hmXhjzXf5p26JcL2qlelSAm8gx7IcwSDBoUbfpJ"
URL = f"https://api.sportradar.com/nhl/trial/v7/en/league/injuries.json?api_key={API_KEY}"

def hae_loukkaantumiset():
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Virhe haettaessa tietoja: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    print("Loukkaantumistiedot haettu onnistuneesti!\n")

    # Tulostetaan tiedot, oletetaan että json on listamuodossa
    for injury in data:
        pelaaja = injury.get("player", {}).get("full_name", "Tuntematon pelaaja")
        joukkue = injury.get("team", {}).get("name", "Tuntematon joukkue")
        kuvaus = injury.get("injury", {}).get("desc", "Ei kuvausta")
        status = injury.get("injury", {}).get("status", "Ei tietoa")
        alkupvm = injury.get("injury", {}).get("start_date", "Ei tietoa")
        print(f"{pelaaja} ({joukkue}): {kuvaus} - Status: {status}, Alkaen: {alkupvm}")

if __name__ == "__main__":
    hae_loukkaantumiset()
