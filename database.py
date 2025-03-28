from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVER_KEY
from datetime import datetime

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVER_KEY)

def add_user(username, chat_id=None):
    """Aggiunge un nuovo utente se non esiste già"""

    existing_user = supabase.table("Users").select("*").eq("username", username).execute()

    if not existing_user.data:
        supabase.table("Users").insert({
            "username": username,
            "chat_id": chat_id
        }).execute()
    elif chat_id and existing_user.data[0].get("chat_id") != chat_id:
        # Update chat_id, if it is changed
        supabase.table("Users").update({"chat_id": chat_id}).eq("username", username).execute()

def add_etf(user, symbol, name, threshold, days):
    """Aggiunge un ETF al tracking per un utente"""

    # Controlla se l'ETF è già monitorato dall'utente
    existing = supabase.table("Etfs").select("*").eq("user", user).eq("symbol", symbol).execute()

    if existing.data:
        # Update etf info if they are changed
        supabase.table("Etfs").update({
            "threshold": threshold,
            "days": days
        }).eq("user", user).eq("symbol", symbol).execute()
    else:
        # Insert new etf
        supabase.table("Etfs").insert({
            "user": user,
            "symbol": symbol,
            "price_max": 0,  # Inizialmente 0, poi verrà aggiornato
            "threshold": threshold,
            "days": days,
            "name": name
        }).execute()

def remove_etf(user, symbol):
    """Rimuove un ETF dal tracking"""
    supabase.table("Etfs").delete().eq("user", user).eq("symbol", symbol).execute()

    # Rimuovi anche tutte le notifiche per questo ETF
    supabase.table("EtfNotifications").delete().eq("user", user).eq("etf_symbol", symbol).execute()

def get_tracked_etfs(user):
    """Restituisce gli ETF monitorati da un utente"""
    result = supabase.table("Etfs").select("*").eq("user", user).execute()
    return result.data

def update_etf_max_price(user, symbol, max_price):
    """Aggiorna il prezzo massimo di un ETF"""

    supabase.table("Etfs").update({
        "price_max": max_price,
        "updated_at": datetime.now().isoformat()
    }).eq("user", user).eq("symbol", symbol).execute()

def get_all_etfs():
    """Restituisce tutti gli ETF monitorati da tutti gli utenti"""
    result = supabase.table("Etfs").select("*").execute()   #TODO: vanno levati doppioni di etf uguali? ci vuole group by sul symbol del'etf?
    return result.data

def get_user_chat_id(username):
    """Restituisce l'ID della chat di un utente"""

    result = supabase.table("Users").select("chat_id").eq("username", username).execute()
    if result.data:
        return result.data[0].get('chat_id')
    return None

def get_all_users():
    """Restituisce tutti gli utenti"""

    result = supabase.table("Users").select("*").execute()
    return result.data

def add_notification(user, etf_symbol, loss_pct):
    """Salva informazioni sull'ultima notifica inviata per un ETF"""

    # Prima cerca se esiste già una notifica per questo ETF
    existing = supabase.table("EtfNotifications").select("*").eq("user", user).eq("etf_symbol", etf_symbol).execute()
    
    now = datetime.now().isoformat()

    if existing.data:
        # Aggiorna la notifica esistente
        supabase.table("EtfNotifications").update({
            "loss_pct": loss_pct,
            "notified_at": now
        }).eq("user", user).eq("etf_symbol", etf_symbol).execute()
    else:
        # Inserisci una nuova notifica
        supabase.table("EtfNotifications").insert({
            "user": user,
            "etf_symbol": etf_symbol,
            "loss_pct": loss_pct,
            "notified_at": now
        }).execute()

def get_last_notification(user, etf_symbol):
    """Restituisce l'ultima notifica inviata per un ETF"""

    result = supabase.table("EtfNotifications").select("*").eq("user", user).eq("etf_symbol", etf_symbol).execute()
    
    if result.data:
        return result.data[0]
    return None
