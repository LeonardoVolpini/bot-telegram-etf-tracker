import time
import schedule
import database as db
import bot
from etf_service import get_etf_price, get_etf_historical_data

def check_etfs_thresholds():
    """
    Controlla tutti gli ETF di tutti gli utenti e invia notifiche
    se un ETF è sceso sotto la soglia impostata
    """
    print("Checking ETF thresholds...")
    
    # Ottieni tutti gli ETF da monitorare
    all_etfs = db.get_all_etfs()
    
    for etf in all_etfs:
        user = etf['user']
        symbol = etf['symbol']
        days = etf['days']
        threshold_pct = etf['threshold']
        
        # Ottieni i dati storici dell'ETF
        historical_data = get_etf_historical_data(symbol, days)
        if not historical_data:
            continue
        
        # Calcola il prezzo massimo nel periodo indicato
        max_price = max(price for _, price in historical_data)
        
        # Ottieni il prezzo attuale
        current_price = get_etf_price(symbol)
        if not current_price:
            continue
        
        # Calcola la perdita percentuale dal massimo
        loss_pct = ((max_price - current_price) / max_price) * 100
        
        # Aggiorna il prezzo massimo nel database
        db.update_etf_max_price(user, symbol, max_price)
        
        # Se la perdita supera la soglia, invia una notifica
        if loss_pct >= threshold_pct:
            message = (
                f"🚨 ALERT! ETF {symbol} has dropped {loss_pct:.2f}% from its {days}-day high!\n"
                f"Maximum price: ${max_price:.2f}\n"
                f"Current price: ${current_price:.2f}\n"
                f"Loss: ${max_price - current_price:.2f} ({loss_pct:.2f}%)"
            )
            
            # Ottieni l'ID della chat dell'utente
            chat_id = db.get_user_chat_id(user)
            if chat_id:
                bot.send_message(chat_id, message)

def start_monitoring():
    """Avvia il monitoraggio degli ETF"""
    
    # Imposta un job per eseguire i controlli ogni ora
    schedule.every(1).hour.do(check_etfs_thresholds)
    
    print("ETF monitoring started. Checking every hour.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Controlla ogni minuto se ci sono jobs da eseguire