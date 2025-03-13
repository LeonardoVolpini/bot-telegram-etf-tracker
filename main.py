import requests
from config import API_URL
from bot import handle_message

URL = f"{API_URL}/getUpdates"

def get_updates(offset=None):
    """Recupera gli aggiornamenti dal bot Telegram."""
    params = {"timeout": 30, "offset": offset}
    response = requests.get(URL, params=params)
    
    if response.status_code == 200:
        return response.json().get("result", [])
    return []

def main():
    print("🤖 Bot ETF Tracker avviato...")
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        
        for update in updates:
            last_update_id = update["update_id"] + 1
            handle_message(update)

if __name__ == "__main__":
    main()
