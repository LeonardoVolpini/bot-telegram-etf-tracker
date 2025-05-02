import time
import schedule
import database as db
import bot
from etf_service import get_etf_price, get_etf_historical_data
from datetime import datetime
from config import MONITORING_INTERVAL

def check_etfs_thresholds():
    """
    Controlla tutti gli ETF di tutti gli utenti e invia notifiche
    se un ETF è sceso sotto la soglia impostata.
    Salta i controlli durante il weekend
    """

    # Ottieni il giorno della settimana
    current_day = datetime.now().weekday()
    if current_day >= 5:  # Skip checks during weekends
        return

    print("Checking ETF thresholds...")
    
    # Ottieni tutti gli ETF da monitorare
    all_etfs = db.get_all_etfs()
    
    for etf in all_etfs:
        user = etf['user']
        symbol = etf['symbol']
        days = etf['days']
        threshold_pct = etf['threshold']
        name = etf['name']
        
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

        # Ottieni l'ultima notifica inviata per questo ETF
        last_notification = db.get_last_notification(user, symbol)
        
        # Aggiorna il prezzo massimo nel database
        db.update_etf_max_price(user, symbol, max_price)

        should_notify = False
        notification_message = ""

        # Se non è mai stata inviata una notifica e la perdita supera la soglia
        if not last_notification and loss_pct >= threshold_pct:
            should_notify = True
            notification_message = (
                f"🚨 ALERT! ETF {symbol} - {name}\n"
                f"Has dropped {loss_pct:.2f}% from its {days}-day high!\n"
                f"Maximum price: ${max_price:.2f}\n"
                f"Current price: ${current_price:.2f}\n"
                f"Loss: ${max_price - current_price:.2f} ({loss_pct:.2f}%)"
            )
        
        # Se è già stata inviata una notifica
        elif last_notification:
            last_notified_loss = last_notification.get('loss_pct', 0)

            # Caso 1: il prezzo è peggiorato di almeno 1% dall'ultima notifica && siamo oltre la soglia
            if loss_pct >= last_notified_loss + 1 and loss_pct >= threshold_pct:
                should_notify = True
                notification_message = (
                    f"📉 UPDATE: ETF {symbol} - {name} \n"
                    f"Has dropped further to {loss_pct:.2f}% from its {days}-day high!\n"
                    f"Maximum price: ${max_price:.2f}\n"
                    f"Current price: ${current_price:.2f}\n"
                    f"Last notified loss: {last_notified_loss:.2f}%\n"
                    f"Additional loss: {(loss_pct - last_notified_loss):.2f}%"
                )

            # Caso 2: il prezzo è migliorato, e ora è almeno 0.5% sopra la soglia
            elif loss_pct <= (threshold_pct - 0.5) and last_notified_loss > threshold_pct:
                should_notify = True
                notification_message = (
                    f"📈 RECOVERY: ETF {symbol} - {name} \n"
                    f"Has improved to {loss_pct:.2f}% from its {days}-day high!\n"
                    f"Maximum price: ${max_price:.2f}\n"
                    f"Current price: ${current_price:.2f}\n"
                    f"Previous loss: {last_notified_loss:.2f}%\n"
                    f"Recovery: {(last_notified_loss - loss_pct):.2f}%"
                )

        # Invio la notifica se necessario
        if should_notify:
            # Get chat id dell'utente
            chat_id = db.get_user_chat_id(user)
            if chat_id:
                bot.send_message(chat_id, notification_message)
                db.add_notification(user, symbol, loss_pct)

def start_monitoring():
    """Avvia il monitoraggio degli ETF"""
    
    # Imposta un job per eseguire i controlli ogni ora
    schedule.every(MONITORING_INTERVAL).hour.do(check_etfs_thresholds)
    
    print("ETF monitoring started. Checking every two hours.")
    
    while True:
        schedule.run_pending()
        time.sleep(MONITORING_INTERVAL)  # Controlla ogni MONITORING_INTERVAL minuti se ci sono jobs da eseguire