import json
import random
import os
from config import TAROT_DECK_FILE, SAVED_SPREADS_FILE

class CardManager:
    _tarot_deck = None
    _saved_spreads = {}

    @classmethod
    def _load_deck(cls):
        if cls._tarot_deck is None:
            with open(TAROT_DECK_FILE, "r", encoding="utf-8") as file:
                cls._tarot_deck = json.load(file)

    @classmethod
    def _load_spreads(cls):
        if os.path.exists(SAVED_SPREADS_FILE):
            with open(SAVED_SPREADS_FILE, "r", encoding="utf-8") as file:
                cls._saved_spreads = json.load(file)

    @classmethod
    def _save_spreads(cls):
        with open(SAVED_SPREADS_FILE, "w", encoding="utf-8") as file:
            json.dump(cls._saved_spreads, file, ensure_ascii=False, indent=4)

    @classmethod
    def generate_spread(cls):
        cls._load_deck()
        all_cards = []
        
        # Добавляем Старшие арканы
        for card_name in cls._tarot_deck["Старшие арканы"].keys():
            all_cards.append(card_name)
            
        # Добавляем Младшие арканы
        for suit, cards in cls._tarot_deck["Младшие арканы"].items():
            for card_name in cards.keys():
                all_cards.append(card_name)
                
        return random.sample(all_cards, 3)

    @classmethod
    def get_card_info(cls, card_name):
        cls._load_deck()
        # Проверяем Старшие арканы
        if card_name in cls._tarot_deck["Старшие арканы"]:
            return cls._tarot_deck["Старшие арканы"][card_name]
            
        # Проверяем Младшие арканы
        for suit, cards in cls._tarot_deck["Младшие арканы"].items():
            if card_name in cards:
                return cards[card_name]
        
        return None

    @classmethod
    def save_spread(cls, user_id, theme, cards):
        cls._load_spreads()
        cls._saved_spreads[user_id] = {"theme": theme, "cards": cards}
        cls._save_spreads()

    @classmethod
    def has_saved_spread(cls, user_id):
        cls._load_spreads()
        return user_id in cls._saved_spreads

    @classmethod
    def get_saved_spread(cls, user_id):
        cls._load_spreads()
        return cls._saved_spreads.get(user_id) 