import time
import json
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from ...utils import fetch_data  

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ekstraklasa/live/scores"  

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "DjangoNotifier")
        try:
            client.connect(BROKER, PORT, 60)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Błąd połączenia z brokerem: {e}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Połączono z {BROKER}."))

        while True:
            try:
                matches = fetch_data()
                
                live_update = []
                if matches:
                    for match in matches:
                        live_update.append({
                            'id': match.get('idEvent'),      
                            'home': match.get('strHomeTeam'),
                            'away': match.get('strAwayTeam'),
                            'homeScore': match.get('intHomeScore'), 
                            'awayScore': match.get('intAwayScore'), 
                            'status': match.get('strStatus')        
                        })

                payload = json.dumps(live_update)
                client.publish(TOPIC, payload)
                

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Błąd: {e}"))

            time.sleep(60)