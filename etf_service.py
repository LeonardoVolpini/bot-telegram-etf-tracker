import requests
from config import ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_URL

def get_etf_price(symbol: str):
    """Recupera il prezzo attuale di un ETF da Alpha Vantage a partire sal suo simbolo."""
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(ALPHA_VANTAGE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            latest_time = list(data["Time Series (5min)"].keys())[0]  # Ultimo timestamp disponibile
            return float(data["Time Series (5min)"][latest_time]["4. close"])  # Prezzo di chiusura
        except (KeyError, IndexError):
            return None
    return None
