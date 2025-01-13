from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import random
import os
from typing import List, Dict, Tuple
from config import IMAGES_PATH
from utils.card_manager import CardManager

class GuessCardGame:
    def __init__(self):
        self.active_games: Dict[int, Dict] = {}  # user_id -> game_data
        self.card_manager = CardManager()
    
    def start_new_game(self, user_id: int) -> Tuple[Dict, List[Dict], InlineKeyboardMarkup]:
        """Начинает новую игру для пользователя."""
        # Получаем все карты
        all_cards = self.card_manager.get_all_cards()
        
        # Выбираем загаданную карту
        target_card = random.choice(all_cards)
        
        # Выбираем 4 случайные карты (исключая загаданную)
        other_cards = [card for card in all_cards if card['en'] != target_card['en']]
        random_cards = random.sample(other_cards, 4)
        
        # Добавляем загаданную карту к случайным
        all_options = random_cards + [target_card]
        # Перемешиваем карты
        random.shuffle(all_options)
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup(row_width=5)
        buttons = []
        for i, card in enumerate(all_options):
            buttons.append(
                InlineKeyboardButton(
                    "🎴",
                    callback_data=f"guess_{i}_{target_card['en'].replace(' ', '_')}"
                )
            )
        keyboard.add(*buttons)
        
        # Сохраняем данные игры
        game_data = {
            "target_card": target_card,
            "options": all_options
        }
        self.active_games[user_id] = game_data
        
        return target_card, all_options, keyboard
    
    def check_guess(self, user_id: int, selected_index: int) -> Tuple[bool, Dict, Dict]:
        """Проверяет угадал ли пользователь карту."""
        if user_id not in self.active_games:
            return False, None, None
        
        game_data = self.active_games[user_id]
        target_card = game_data["target_card"]
        selected_card = game_data["options"][selected_index]
        
        is_correct = selected_card['en'] == target_card['en']
        
        # Очищаем данные игры
        del self.active_games[user_id]
        
        return is_correct, target_card, selected_card

def get_try_again_keyboard():
    """Создает клавиатуру с кнопкой 'Попробовать еще раз'."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("🎲 Попробовать еще раз"),
        KeyboardButton("🔮 Вернуться к гаданию")
    )
    return keyboard 