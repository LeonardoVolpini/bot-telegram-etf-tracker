import requests
import threading
import time
from config import API_URL
from bot import handle_message
from monitor import start_monitoring

URL = f"{API_URL}/getUpdates"

def get_updates(offset=None):
    """Recupera gli aggiornamenti dal bot Telegram."""

    params = {"timeout": 30}
    if offset:
        params["offset"] = offset

    try:
        response = requests.get(URL, params=params)

        if response.status_code == 200:
            return response.json().get("result", [])
        print(f"Error fetching updates: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Exception while getting updates: {e}")
        
    return []

def telegram_polling():
    """Funzione che gestisce il polling degli aggiornamenti Telegram"""
    
    print("🤖 Starting Telegram polling...")
    last_update_id = None

    while True:
        try:
            updates = get_updates(last_update_id)
            
            for update in updates:
                last_update_id = update["update_id"] + 1
                handle_message(update)
        except Exception as e:
            print(f"Error in polling loop: {e}")
            time.sleep(5)  # Breve pausa in caso di errore

def main():
    print("🤖 ETF Tracker Bot starting up...")
    
    # Avvia il polling di Telegram in un thread separato
    telegram_thread = threading.Thread(target=telegram_polling)
    telegram_thread.daemon = True  # Il thread terminerà quando termina il programma principale
    telegram_thread.start()
    
    # Avvia il monitoraggio degli ETF nel thread principale
    start_monitoring()

if __name__ == "__main__":
    main()