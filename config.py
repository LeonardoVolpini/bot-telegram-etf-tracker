import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVER_KEY = os.getenv("SUPABASE_SERVER_KEY")

# URL di base
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Configuration for monitoring
MONITORING_INTERVAL = 60  # minutes