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

    symbol = _get_valid_symbol(symbol)
    if not symbol:
        print("Invalid ETF symbol")
        return None

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        ticker = yf.Ticker(symbol)
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
    """Verifica se un simbolo ETF è valido e restituisce il simbolo corretto se trovato."""

    valid_symbol = _get_valid_symbol(symbol)
    return valid_symbol is not None
    

def get_etf_info(symbol: str):
    """Ottiene informazioni dettagliate su un ETF."""

    symbol = _get_valid_symbol(symbol)
    if not symbol:
        return None

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'name': info.get('longName', 'N/A'),
            'symbol': symbol,  # Restituisce il simbolo corretto con il suffisso della borsa
            'currency': info.get('currency', 'N/A'),
            'exchange': info.get('exchange', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'description': info.get('longBusinessSummary', 'N/A')
        }
    except Exception as e:
        print(f"Error getting info for {symbol}: {e}")
        return None
    
def _get_valid_symbol(symbol):
    """Ottiene un simbolo valido per Yahoo Finance."""

    # Prima prova il simbolo esatto
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Verifica se abbiamo ricevuto dati validi
        if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
            return symbol
    except:
        pass
    
    # Se non funziona, prova le varianti
    return _try_symbol_variants(symbol)

def _try_symbol_variants(base_symbol):
    """Prova diverse varianti di suffissi per borse europee."""

    # Lista di suffissi comuni per le borse europee
    exchange_suffixes = [
        '.L',   # London
        '.MI',  # Milano
        '.PA',  # Parigi
        '.DE',  # Germania
        '.AS',  # Amsterdam
        '.BR',  # Bruxelles
        '.MC',  # Madrid
        '.VI',  # Vienna
        '.SW',  # Svizzera
        '.ST',  # Stoccolma
        '.CO',  # Copenhagen
        '.HE',  # Helsinki
        '.LS',  # Lisbona
        '.IR',  # Irlanda
        '.F',   # Francoforte
        '.MU',  # Monaco
        '',     # Senza suffisso
    ]
    
    for suffix in exchange_suffixes:
        try:
            test_symbol = f"{base_symbol}{suffix}"
            ticker = yf.Ticker(test_symbol)
            info = ticker.info
            
            # Verifica se abbiamo ricevuto dati validi
            if 'regularMarketPrice' in info and info['regularMarketPrice'] is not None:
                print(f"Simbolo valido trovato: {test_symbol}")
                return test_symbol
        except Exception as e:
            continue
    
    return None