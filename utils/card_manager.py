import json
import random
import os
from config import TAROT_DECK_FILE, SAVED_SPREADS_FILE
from typing import List, Dict
import logging

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

    @staticmethod
    def get_all_cards() -> List[Dict]:
        """Возвращает список всех карт из колоды."""
        try:
            with open(TAROT_DECK_FILE, 'r', encoding='utf-8') as file:
                deck = json.load(file)
                all_cards = []
                
                # Словарь соответствия русских названий английским
                name_mapping = {
                    # Старшие арканы
                    "Шут": "The Fool",
                    "Маг": "The Magician",
                    "Верховная Жрица": "The High Priestess",
                    "Императрица": "The Empress",
                    "Император": "The Emperor",
                    "Иерофант": "The Hierophant",
                    "Влюбленные": "The Lovers",
                    "Колесница": "The Chariot",
                    "Сила": "Strength",
                    "Отшельник": "The Hermit",
                    "Колесо Фортуны": "Wheel of Fortune",
                    "Справедливость": "Justice",
                    "Повешенный": "The Hanged Man",
                    "Смерть": "Death",
                    "Умеренность": "Temperance",
                    "Дьявол": "The Devil",
                    "Башня": "The Tower",
                    "Звезда": "The Star",
                    "Луна": "The Moon",
                    "Солнце": "The Sun",
                    "Суд": "Judgement",
                    "Мир": "The World",
                    
                    # Младшие арканы - Жезлы
                    "Туз Жезлов": "Ace of Wands",
                    "Двойка Жезлов": "Two of Wands",
                    "Тройка Жезлов": "Three of Wands",
                    "Четверка Жезлов": "Four of Wands",
                    "Пятерка Жезлов": "Five of Wands",
                    "Шестерка Жезлов": "Six of Wands",
                    "Семерка Жезлов": "Seven of Wands",
                    "Восьмерка Жезлов": "Eight of Wands",
                    "Девятка Жезлов": "Nine of Wands",
                    "Десятка Жезлов": "Ten of Wands",
                    "Паж Жезлов": "Page of Wands",
                    "Рыцарь Жезлов": "Knight of Wands",
                    "Королева Жезлов": "Queen of Wands",
                    "Король Жезлов": "King of Wands",
                    
                    # Младшие арканы - Кубки
                    "Туз Кубков": "Ace of Cups",
                    "Двойка Кубков": "Two of Cups",
                    "Тройка Кубков": "Three of Cups",
                    "Четверка Кубков": "Four of Cups",
                    "Пятерка Кубков": "Five of Cups",
                    "Шестерка Кубков": "Six of Cups",
                    "Семерка Кубков": "Seven of Cups",
                    "Восьмерка Кубков": "Eight of Cups",
                    "Девятка Кубков": "Nine of Cups",
                    "Десятка Кубков": "Ten of Cups",
                    "Паж Кубков": "Page of Cups",
                    "Рыцарь Кубков": "Knight of Cups",
                    "Королева Кубков": "Queen of Cups",
                    "Король Кубков": "King of Cups",
                    
                    # Младшие арканы - Мечи
                    "Туз Мечей": "Ace of Swords",
                    "Двойка Мечей": "Two of Swords",
                    "Тройка Мечей": "Three of Swords",
                    "Четверка Мечей": "Four of Swords",
                    "Пятерка Мечей": "Five of Swords",
                    "Шестерка Мечей": "Six of Swords",
                    "Семерка Мечей": "Seven of Swords",
                    "Восьмерка Мечей": "Eight of Swords",
                    "Девятка Мечей": "Nine of Swords",
                    "Десятка Мечей": "Ten of Swords",
                    "Паж Мечей": "Page of Swords",
                    "Рыцарь Мечей": "Knight of Swords",
                    "Королева Мечей": "Queen of Swords",
                    "Король Мечей": "King of Swords",
                    
                    # Младшие арканы - Пентакли
                    "Туз Пентаклей": "Ace of Pentacles",
                    "Двойка Пентаклей": "Two of Pentacles",
                    "Тройка Пентаклей": "Three of Pentacles",
                    "Четверка Пентаклей": "Four of Pentacles",
                    "Пятерка Пентаклей": "Five of Pentacles",
                    "Шестерка Пентаклей": "Six of Pentacles",
                    "Семерка Пентаклей": "Seven of Pentacles",
                    "Восьмерка Пентаклей": "Eight of Pentacles",
                    "Девятка Пентаклей": "Nine of Pentacles",
                    "Десятка Пентаклей": "Ten of Pentacles",
                    "Паж Пентаклей": "Page of Pentacles",
                    "Рыцарь Пентаклей": "Knight of Pentacles",
                    "Королева Пентаклей": "Queen of Pentacles",
                    "Король Пентаклей": "King of Pentacles"
                }
                
                # Добавляем Старшие арканы
                logging.info("Загрузка Старших арканов:")
                for card_name, card_info in deck["Старшие арканы"].items():
                    card_info['en'] = name_mapping.get(card_name, card_name)  # Используем английское название
                    logging.info(f"Добавлена карта: {card_name} -> {card_info['en']}")
                    all_cards.append(card_info)
                
                # Добавляем Младшие арканы
                logging.info("Загрузка Младших арканов:")
                for suit, cards in deck["Младшие арканы"].items():
                    for card_name, card_info in cards.items():
                        card_info['en'] = name_mapping.get(card_name, card_name)  # Используем английское название
                        logging.info(f"Добавлена карта: {card_name} -> {card_info['en']}")
                        all_cards.append(card_info)
                
                logging.info(f"Всего загружено карт: {len(all_cards)}")
                return all_cards
        except Exception as e:
            logging.error(f"Ошибка при загрузке карт: {e}")
            return [] 