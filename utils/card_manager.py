import random
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from .database import Database
from .cache_manager import CacheManager

class CardManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CardManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self.db = Database()
            self.cache = CacheManager()
            self._initialized = True
            self.cards = []
            self.card_names = []

    async def initialize(self):
        """Асинхронная инициализация менеджера."""
        await self._load_cards()

    async def _load_cards(self):
        """Загрузка списка карт в память."""
        try:
            with open('data/tarot_deck.json', 'r', encoding='utf-8') as f:
                deck_data = json.load(f)
                self.cards = []
                self.card_names = []
                
                # Загружаем Старшие арканы
                for ru_name, card_data in deck_data["Старшие арканы"].items():
                    name_mapping = {
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
                    }
                    en_name = name_mapping.get(ru_name, ru_name)
                    card_data['en'] = en_name
                    card_data['ru'] = ru_name
                    self.cards.append(card_data)
                    self.card_names.append(en_name)
                    # Кэшируем карту
                    await self.cache.set(f"card_{en_name}", card_data)
                
                # Загружаем Младшие арканы
                for suit, cards in deck_data["Младшие арканы"].items():
                    for ru_name, card_data in cards.items():
                        parts = ru_name.split()
                        if len(parts) >= 2:
                            rank = parts[0]
                            rank_map = {
                                "Туз": "Ace",
                                "Двойка": "Two",
                                "Тройка": "Three",
                                "Четверка": "Four",
                                "Пятерка": "Five",
                                "Шестерка": "Six",
                                "Семерка": "Seven",
                                "Восьмерка": "Eight",
                                "Девятка": "Nine",
                                "Десятка": "Ten",
                                "Паж": "Page",
                                "Рыцарь": "Knight",
                                "Королева": "Queen",
                                "Король": "King"
                            }
                            suit_map = {
                                "Жезлов": "Wands",
                                "Кубков": "Cups",
                                "Мечей": "Swords",
                                "Пентаклей": "Pentacles"
                            }
                            en_rank = rank_map.get(rank, rank)
                            en_suit = suit_map.get(parts[-1], parts[-1])
                            en_name = f"{en_rank} of {en_suit}"
                        else:
                            en_name = ru_name
                            
                        card_data['en'] = en_name
                        card_data['ru'] = ru_name
                        self.cards.append(card_data)
                        self.card_names.append(en_name)
                        # Кэшируем карту
                        await self.cache.set(f"card_{en_name}", card_data)
                
                # Кэшируем список всех карт
                await self.cache.set("all_cards", self.cards)
                await self.cache.set("card_names", self.card_names)
                
                logging.info(f"Загружено {len(self.cards)} карт")
                
        except Exception as e:
            logging.error(f"Ошибка при загрузке колоды карт: {e}")
            self.cards = []
            self.card_names = []

    def get_all_cards(self) -> List[Dict]:
        """Возвращает список всех карт."""
        return self.cards

    async def get_card_info(self, name_en: str) -> Optional[Dict]:
        """Получение информации о карте."""
        # Пробуем получить из кэша
        cache_key = f"card_{name_en}"
        card_info = await self.cache.get(cache_key)
        if card_info:
            return card_info

        # Если нет в кэше, ищем в локальном списке
        for card in self.cards:
            if card['en'] == name_en:
                # Сохраняем в кэш
                await self.cache.set(cache_key, card)
                return card

        # Если не нашли, ищем в базе данных
        card_info = await self.db.get_card(name_en)
        if card_info:
            # Сохраняем в кэш
            await self.cache.set(cache_key, card_info)
        return card_info

    def generate_spread(self) -> List[str]:
        """Генерация расклада из трех случайных карт."""
        if not self.card_names:
            return []
        return random.sample(self.card_names, 3)

    async def save_spread(self, user_id: str, theme: str, cards: List[str]) -> bool:
        """Сохранение расклада в базу данных."""
        try:
            async with self._lock:
                await self.db.save_spread(int(user_id), theme, json.dumps(cards))
                # Кэшируем последний расклад пользователя
                await self.cache.set(f"last_spread_{user_id}", {
                    "theme": theme,
                    "cards": cards,
                    "timestamp": datetime.now().isoformat()
                })
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении расклада: {e}")
            return False

    async def get_saved_spread(self, user_id: str) -> Optional[Dict]:
        """Получение последнего сохраненного расклада пользователя."""
        try:
            # Пробуем получить из кэша
            cache_key = f"last_spread_{user_id}"
            spread = await self.cache.get(cache_key)
            if spread:
                return spread

            # Если нет в кэше, получаем из базы
            spread = await self.db.get_last_spread(int(user_id))
            if spread:
                # Сохраняем в кэш
                await self.cache.set(cache_key, spread)
            return spread
        except Exception as e:
            logging.error(f"Ошибка при получении сохраненного расклада: {e}")
            return None

    async def get_random_card(self) -> Optional[Dict]:
        """Получение случайной карты."""
        if not self.card_names:
            return None
        random_card_name = random.choice(self.card_names)
        return await self.get_card_info(random_card_name)

    @staticmethod
    def has_saved_spread(user_id: str) -> bool:
        """Проверка наличия сохраненного расклада."""
        # В новой версии эта функция будет асинхронной
        # Пока оставляем заглушку для обратной совместимости
        return False 