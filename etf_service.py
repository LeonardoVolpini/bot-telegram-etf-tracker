import requests
from datetime import datetime, timedelta
from config import ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_URL

def get_etf_price(symbol: str):
    """Recupera il prezzo attuale di un ETF da Alpha Vantage a partire dal suo simbolo."""
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(ALPHA_VANTAGE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            return float(data["Global Quote"]["05. price"])
        except (KeyError, ValueError):
            print(f"Error getting price for {symbol}: {data}")
            return None
        
    print(f"Error fetching data for {symbol}: Status code {response.status_code}")
    return None

def get_etf_historical_data(symbol: str, days: int):
    """
    Recupera i dati storici di un ETF per il numero di giorni specificato.
    Restituisce una lista di tuple (data, prezzo).
    """

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact" if days <= 100 else "full",
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    response = requests.get(ALPHA_VANTAGE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        try:
            time_series = data["Time Series (Daily)"]

            # Filtra per i giorni richiesti
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            historical_data = []
            for date, values in time_series.items():
                if date >= cutoff_date:
                    historical_data.append((date, float(values["4. close"])))
            
            return historical_data
        except (KeyError, ValueError) as e:
            print(f"Error getting historical data for {symbol}: {e}")
            return None
        
    print(f"Error fetching historical data for {symbol}: Status code {response.status_code}")
    return None


def validate_etf_symbol(symbol: str):
    """Verifica se un simbolo ETF è valido."""
    return get_etf_price(symbol) is not None