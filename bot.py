import requests
from config import API_URL
from etf_service import get_etf_price


# Dizionario per tenere traccia degli ETF monitorati per ogni utente
user_tracking = {}


def send_message(chat_id, text):
    """Invia un messaggio Telegram"""

    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    
    requests.post(url, json=payload)


def start(update):
    """Messaggio di benvenuto"""

    chat_id = update["message"]["chat"]["id"]
    send_message(chat_id, "Hi! I'm your bot for monitoring ETFs.\n"
                            "I will help you get instant notifications when an ETF goes down by x % from its high of the last y days.\n"
                            "Use /help to see the available commands.")
    

def help(update):
    """Lista dei comandi disponibili"""

    chat_id = update["message"]["chat"]["id"]
    send_message(chat_id, "/start - Start the bot\n"
                            "/help - Get help with the bot\n"
                            "/track <etf_symbol> <percentage_threshold> <days_back>\n"
                            "/remove <etf_symbol> - Stop tracking an ETF\n")
    

def track_etf(update):
    """Aggiunge un ETF al tracking"""

    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"].split()

    if len(text) != 4:
        send_message(chat_id, "⚠️ Use command: /track <etf_symbol> <threshold> <days>")
        return
    
    symbol, threshold, days = text[1].upper(), text[2], text[3]

    try:
        threshold = float(threshold)
        days = int(days)
    except ValueError:
        send_message(chat_id, "❌ Threshold must be a float number and days must be an integer number!")
        return

    if chat_id not in user_tracking:
        user_tracking[chat_id] = {}

    user_tracking[chat_id][symbol] = {"threshold": threshold, "days": days}
    send_message(chat_id, f"✅ Now you're tracking {symbol}: {threshold}% loss in last {days} days")


def remove_etf(update):
    """Rimuove un ETF dal monitoraggio."""

    chat_id = update["message"]["chat"]["id"]
    text = update["message"]["text"].split()

    if len(text) != 2:
        send_message(chat_id, "⚠️ Use command: /remove <etf_symbol>")
        return

    symbol = text[1].upper()

    if chat_id in user_tracking and symbol in user_tracking[chat_id]:
        del user_tracking[chat_id][symbol]
        send_message(chat_id, f"🚀 {symbol} removed from tracking!")
    else:
        send_message(chat_id, "❌ ETF was not in tracking status")



def etfs(update):
    """Mostra gli ETF attualmente monitorati."""

    chat_id = update["message"]["chat"]["id"]
    if chat_id not in user_tracking or not user_tracking[chat_id]:
        send_message(chat_id, "📉 You are not tracking any ETFs.")
        return
    
    message = "📈 Currently tracking:\n"
    for etf, details in user_tracking[chat_id].items():
        message += f"{etf}: {details['threshold']}% loss in last {details['days']} days\n"
    
    send_message(chat_id, message)

def handle_message(update):
    """Gestisce i messaggi ricevuti dal bot."""
    
    text = update["message"]["text"].lower().strip()

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
        send_message(update["message"]["chat"]["id"], "⚠️ Unknown command. Use /help for see list of commands.")
