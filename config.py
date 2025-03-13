import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# URL di base
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"