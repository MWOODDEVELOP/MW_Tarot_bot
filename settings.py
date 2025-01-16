import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [599081669]  # Список ID администраторов
MAX_DAILY_SPREADS = 3  # Максимальное количество раскладов в день

# Paths
TAROT_DECK_FILE = "data/tarot_deck.json"
SAVED_SPREADS_FILE = "data/saved_spreads.json"
IMAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", "tarot")
USER_DATA_FILE = "data/user_data.json"

# User preferences
DEFAULT_THEME = "light"
SHOW_CARD_IMAGES = True 