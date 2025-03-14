from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVER_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVER_KEY)

def add_user(username):
    """Aggiunge un nuovo utente se non esiste già"""

    existing_user = supabase.table("Users").select("*").eq("username", username).execute()
    if not existing_user.data:
        supabase.table("Users").insert({"username": username}).execute()

def add_etf(user, symbol, threshold, days):
    """Aggiunge un ETF al tracking per un utente"""

    supabase.table("Etfs").insert({
        "user": user,
        "symbol": symbol,
        "price_max": 0,  # Inizialmente 0, poi verrà aggiornato
        "threshold": threshold,
        "days": days
    }).execute()

def remove_etf(user, symbol):
    """Rimuove un ETF dal tracking"""
    supabase.table("Etfs").delete().eq("user", user).eq("symbol", symbol).execute()

def get_tracked_etfs(user):
    """Restituisce gli ETF monitorati da un utente"""
    result = supabase.table("Etfs").select("*").eq("user", user).execute()
    return result.data
