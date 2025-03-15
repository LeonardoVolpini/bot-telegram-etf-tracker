import yfinance as yf
from datetime import datetime, timedelta

def get_etf_price(symbol: str):
    """Recupera il prezzo attuale di un ETF da Yahoo Finance, tramite yfinance, partire dal suo simbolo."""

    try:
        ticker = yf.Ticker(symbol)

        # Get last available price
        price = ticker.history(period="1d")

        if price.empty:
            print(f"No data available for {symbol}")
            return None
        
        return float(price["Close"].iloc[-1])
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return None

def get_etf_historical_data(symbol: str, days: int):
    """
    Recupera i dati storici di un ETF per il numero di giorni specificato.
    Restituisce una lista di tuple (data, prezzo).
    """

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        ticker = yf.Ticker(symbol=symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            print(f"No historical data available for {symbol}")
            return None
        
        # Converti in lista di tuple (data, prezzo di chiusura)
        historical_data = []
        for date, row in data.iterrows():
            historical_data.append((date.strftime('%Y-%m-%d'), float(row['Close'])))
        
        return historical_data[-min(days, len(historical_data)):]
    except Exception as e:
        print(f"Error getting historical data for {symbol}: {e}")
        return None


def validate_etf_symbol(symbol: str):
    """Verifica se un simbolo ETF è valido."""
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        return 'longName' in info and info['longName'] is not None
    except:
        return False
    

def get_etf_info(symbol: str):
    """Ottiene informazioni dettagliate su un ETF."""
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'name': info.get('longName', 'N/A'),
            'currency': info.get('currency', 'N/A'),
            'exchange': info.get('exchange', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'description': info.get('longBusinessSummary', 'N/A')
        }
    except Exception as e:
        print(f"Error getting info for {symbol}: {e}")
        return None