import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
LEAGUE_ID = "4422" 
SEASON = "2025-2026"

BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"

def fetch_data():
    url = f"{BASE_URL}/eventsnextleague.php?id={LEAGUE_ID}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('events') or []
    except Exception as e:
        print(f"Error {e}")
        return []


def fetch_league_table():

    url = f"{BASE_URL}/lookuptable.php?l={LEAGUE_ID}&s={SEASON}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('table', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def fetch_last_events():

    url = f"{BASE_URL}/eventspastleague.php?id={LEAGUE_ID}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('events', [])
    except Exception as e:
        print(f"Error: {e}")
        return []