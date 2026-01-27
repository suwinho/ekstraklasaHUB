import requests
import os
import paho.mqtt.client as mqtt
import json
from dotenv import load_dotenv
from datetime import datetime

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
    
def fetch_team_details(team_name):
    formatted_name = team_name.lower().replace(' ', '_')
    
    url = f"{BASE_URL}/searchteams.php?t={formatted_name}"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        teams = data.get('teams')
        
        if teams:
            for team in teams:
                if team.get('strSport') == 'Soccer':
                    return team
            
            return teams[0]
        else:
            return None
            
    except Exception as e:
        print(f"Błąd pobierania szczegółów drużyny: {e}")
        return None

def fetch_last_matches(team_id):
    url = f"{BASE_URL}/eventslast.php?id={team_id}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('results') or []
    except Exception as e:
        print(f"Błąd pobierania meczów: {e}")
        return []
    
def send_prediction_notification(username, match, action="zaktualizował typ"):
    try:
        broker = "broker.hivemq.com"
        port = 1883
        topic = "ekstraklasa/notifications" 
        
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "DjangoNotifier")
        client.connect(broker, port, 60)
        
        message = {
            "type": "notification",
            "text": f"Użytkownik {username} {action} na mecz {match}!"
        }
        
        client.publish(topic, json.dumps(message))
        client.disconnect()
    except Exception as e:
        print(f"Błąd: {e}")


def write_logs_to_file(str): 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {str}\n"
    with open('logs.txt', 'a') as f:
        f.write(msg)
  
