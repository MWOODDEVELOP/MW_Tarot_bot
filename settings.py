from typing import List, Dict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Bot settings
    BOT_TOKEN: str = "YOUR_BOT_TOKEN"
    ADMIN_IDS: List[int] = [123456789]  # Список ID администраторов
    MAX_DAILY_SPREADS: int = 3  # Максимальное количество раскладов в день
    
    # Paths
    TAROT_DECK_FILE: str = "data/tarot_deck.json"
    SAVED_SPREADS_FILE: str = "data/saved_spreads.json"
    IMAGES_PATH: str = "images/tarot/"
    USER_DATA_FILE: str = "data/user_data.json"
    
    # User preferences
    DEFAULT_THEME: str = "light"
    SHOW_CARD_IMAGES: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings() 