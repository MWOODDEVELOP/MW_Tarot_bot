import json
from datetime import datetime
from typing import Dict, Optional
from settings import settings

class UserManager:
    def __init__(self):
        self.users: Dict = self._load_users()
    
    def _load_users(self) -> Dict:
        try:
            with open(settings.USER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_users(self):
        with open(settings.USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=4)
    
    def get_user(self, user_id: int) -> Dict:
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                "spreads_today": 0,
                "last_spread_date": None,
                "theme": settings.DEFAULT_THEME,
                "show_images": settings.SHOW_CARD_IMAGES,
                "daily_prediction": False,
                "last_daily_prediction": None
            }
            self._save_users()
        return self.users[str(user_id)]
    
    def can_make_spread(self, user_id: int) -> bool:
        if user_id in settings.ADMIN_IDS:
            return True
            
        user = self.get_user(user_id)
        today = datetime.now().date()
        last_spread = datetime.fromisoformat(user["last_spread_date"]) if user["last_spread_date"] else None
        
        if not last_spread or last_spread.date() != today:
            user["spreads_today"] = 0
            user["last_spread_date"] = datetime.now().isoformat()
            self._save_users()
            return True
            
        return user["spreads_today"] < settings.MAX_DAILY_SPREADS
    
    def increment_spreads(self, user_id: int):
        if user_id in settings.ADMIN_IDS:
            return
            
        user = self.get_user(user_id)
        user["spreads_today"] += 1
        user["last_spread_date"] = datetime.now().isoformat()
        self._save_users()
    
    def update_preferences(self, user_id: int, theme: Optional[str] = None, show_images: Optional[bool] = None):
        user = self.get_user(user_id)
        if theme is not None:
            user["theme"] = theme
        if show_images is not None:
            user["show_images"] = show_images
        self._save_users()
    
    def toggle_daily_prediction(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        user["daily_prediction"] = not user["daily_prediction"]
        self._save_users()
        return user["daily_prediction"]
    
    def get_daily_prediction_subscribers(self) -> list:
        return [int(user_id) for user_id, data in self.users.items() 
                if data.get("daily_prediction", False)] 