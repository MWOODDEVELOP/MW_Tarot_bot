import json
import logging
from typing import Dict, Optional, List
from config import TAROT_DECK_FILE

class AdminCardEditor:
    def __init__(self):
        self.deck = self._load_deck()
        
    def _load_deck(self) -> Dict:
        """Загружает колоду из файла."""
        try:
            with open(TAROT_DECK_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка при загрузке колоды: {e}")
            return {}
            
    def _save_deck(self) -> bool:
        """Сохраняет колоду в файл."""
        try:
            with open(TAROT_DECK_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.deck, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении колоды: {e}")
            return False
            
    def get_card_info(self, card_name: str) -> Optional[Dict]:
        """Получает информацию о карте."""
        # Проверяем в Старших арканах
        if card_name in self.deck["Старшие арканы"]:
            return self.deck["Старшие арканы"][card_name]
            
        # Проверяем в Младших арканах
        for suit, cards in self.deck["Младшие арканы"].items():
            if card_name in cards:
                return cards[card_name]
        return None
        
    def update_card(self, card_name: str, field: str, value: str) -> bool:
        """Обновляет поле карты."""
        try:
            card = self.get_card_info(card_name)
            if card:
                card[field] = value
                return self._save_deck()
            return False
        except Exception as e:
            logging.error(f"Ошибка при обновлении карты: {e}")
            return False
            
    def get_all_fields(self) -> List[str]:
        """Возвращает список всех возможных полей карты."""
        return [
            "history",
            "Финансы",
            "Отношения",
            "Карьера",
            "Карта на сегодня",
            "Карта на неделю",
            "Карта на месяц"
        ]
        
    def get_all_cards(self) -> List[str]:
        """Возвращает список всех карт."""
        cards = []
        # Добавляем Старшие арканы
        cards.extend(self.deck["Старшие арканы"].keys())
        # Добавляем Младшие арканы
        for suit, suit_cards in self.deck["Младшие арканы"].items():
            cards.extend(suit_cards.keys())
        return sorted(cards) 