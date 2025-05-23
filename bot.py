import requests
from config import API_URL
from etf_service import get_etf_price, get_etf_info
import database as db


def send_message(chat_id, text):
    """Invia un messaggio Telegram"""

    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Error sending message: {response.text}")
    except Exception as e:
        print(f"Failed to send message: {e}")


def start(update):
    """Messaggio di benvenuto"""

    chat_id = update["message"]["chat"]["id"]
    username = update["message"]["chat"]["username"]

    db.add_user(username, chat_id)
    send_message(chat_id, "Hi! I'm your bot for monitoring ETFs.\n"
                            "I will help you get instant notifications when an ETF goes down by x % from its high of the last y days.\n"
                            "Use /help to see the available commands.")
    

def help(update):
    """Lista dei comandi disponibili"""

    chat_id = update["message"]["chat"]["id"]
    send_message(chat_id, "/start - Start the bot\n"
                            "/help - Get help with the bot\n"
                            "/track <etf_symbol> <percentage_threshold> <days_back>\n"
                            "/remove <etf_symbol> - Stop tracking an ETF\n"
                            "/etfs - List the ETFs you're tracking\n\n"
                            "Example: /track SPY 10 30\n"
                            "This will notify you when SPY drops 10% from its 30-day high.")
    

def track_etf(update):
    """Aggiunge un ETF al tracking"""

    chat_id = update["message"]["chat"]["id"]
    username = update["message"]["chat"]["username"]
    text = update["message"]["text"].split()

    if len(text) != 4:
        send_message(chat_id, "⚠️ Usage: /track <etf_symbol> <threshold> <days>"
                                "Example: /track SPY 10 30")
        return
    
    base_symbol = text[1].upper()
    threshold, days = text[2], text[3]

    try:
        threshold = float(threshold)
        days = int(days)

        if threshold <=0 or threshold > 100:
            raise ValueError("Threshold must be between 0 and 100")
        if days <= 0:
            raise ValueError("Days must be a positive integer number")
        if days > 365:
            send_message(chat_id, "❌ Maximum tracking period is 365 days")
            return
        
    except ValueError:
        send_message(chat_id, "❌ Threshold must be a positive number and days must be a positive integer!")
        return
    
    # Invia messaggio per far sapere all'utente che stiamo cercando l'ETF
    send_message(chat_id, f"🔍 Searching for ETF {base_symbol}...")

    # Ottieni informazioni sull'ETF
    etf_info = get_etf_info(base_symbol)

    if not etf_info:
        send_message(chat_id, f"❌ Could not find ETF with symbol '{base_symbol}'. Please check and try again.")
        return

    # Usa il simbolo corretto (che potrebbe includere un suffisso di borsa)
    correct_symbol = etf_info['symbol']

    db.add_etf(username, correct_symbol, etf_info['name'], threshold, days)
    send_message(chat_id, f"✅ Now tracking {correct_symbol}: {etf_info['name']}\n"
                            f"Will notify when it drops {threshold}% from its {days}-day high.")


def remove_etf(update):
    """Rimuove un ETF dal monitoraggio."""

    chat_id = update["message"]["chat"]["id"]
    username = update["message"]["chat"]["username"]
    text = update["message"]["text"].split()

    if len(text) != 2:
        send_message(chat_id, "⚠️ Usage: /remove <etf_symbol>")
        return
    
    symbol = text[1].upper()
    
    # Verifica che l'utente stia effettivamente monitorando questo ETF
    etfs = db.get_tracked_etfs(username)
    if not any(etf['symbol'] == symbol for etf in etfs):
        send_message(chat_id, f"❌ You're not tracking {symbol}")
        return

    db.remove_etf(username, symbol)
    send_message(chat_id, f"✅ {symbol} removed from tracking!")



def etfs(update):
    """Mostra gli ETF attualmente monitorati."""

    chat_id = update["message"]["chat"]["id"]
    username = update["message"]["chat"]["username"]
    
    etfs = db.get_tracked_etfs(username)
    if not etfs:
        send_message(chat_id, "You are not tracking any ETFs.")
        return
    
    message = "📈 Your tracked ETFs:\n\n"
    for etf in etfs:
        symbol = etf['symbol']
        threshold = etf['threshold']
        days = etf['days']
        name = etf['name']
        price_max = etf['price_max'] if etf['price_max'] > 0 else "Calculating..."

         # Ottieni il prezzo attuale se il prezzo massimo è stato calcolato
        if etf['price_max'] > 0:
            current_price = get_etf_price(symbol)
            if current_price:
                loss_pct = ((etf['price_max'] - current_price) / etf['price_max']) * 100
                message += f"{symbol} - {name}:\n {threshold}% threshold over {days} days\n"
                message += f"  Max: ${price_max:.2f}, Current: ${current_price:.2f}\n"
                message += f"  Current loss: {loss_pct:.2f}%\n\n"
            else:
                message += f"{symbol} - {name}:\n {threshold}% threshold over {days} days\n"
                message += f"  Max: ${price_max:.2f}, Current: Unable to fetch\n\n"
        else:
            message += f"{symbol} - {name}:\n {threshold}% threshold over {days} days\n"
            message += f"  Status: Setting up tracking...\n\n"
    
    send_message(chat_id, message)

def handle_message(update):
    """Gestisce i messaggi ricevuti dal bot."""

    chat_id = update["message"]["chat"]["id"]
    username = update["message"]["chat"]["username"]
    text = update["message"]["text"].lower().strip()

    user = db.get_user_chat_id(username)
    if not user and text != "/start":
        send_message(chat_id,"⚠️ Please start the bot using /start before using other commands.")
        return

    if text == "/start":
        start(update)
    elif text == "/help":
        help(update)
    elif text.startswith("/track"):
        track_etf(update)
    elif text.startswith("/remove"):
        remove_etf(update)
    elif text == "/etfs":
        etfs(update)    
    else:
        send_message(update["message"]["chat"]["id"], "⚠️ Unknown command. Use /help to see available commands.")
