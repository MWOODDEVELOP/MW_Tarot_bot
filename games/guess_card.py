from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from typing import Dict, List, Tuple
from utils.card_manager import CardManager

class GuessCardGame:
    def __init__(self):
        self.card_manager = CardManager()
        self.current_games = {}  # {user_id: {"target_card": card, "options": [cards]}}

    def start_new_game(self, user_id: int) -> Tuple[Dict, List[Dict], InlineKeyboardMarkup]:
        """Начинает новую игру для пользователя."""
        all_cards = self.card_manager.get_all_cards()
        
        # Выбираем случайную карту
        target_card = random.choice(all_cards)
        
        # Выбираем 4 случайные карты (не включая целевую)
        other_cards = [card for card in all_cards if card['en'] != target_card['en']]
        options = random.sample(other_cards, 4)
        
        # Добавляем целевую карту в случайную позицию
        insert_pos = random.randint(0, 4)
        options.insert(insert_pos, target_card)
        
        # Сохраняем состояние игры
        self.current_games[user_id] = {
            "target_card": target_card,
            "options": options
        }
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup(row_width=1)
        for i, card in enumerate(options):
            keyboard.add(InlineKeyboardButton(
                f"🎴 Карта {i + 1}",
                callback_data=f"guess_{i}"
            ))
        
        return target_card, options, keyboard

    def check_guess(self, user_id: int, selected_index: int) -> Tuple[bool, Dict, Dict]:
        """Проверяет угадал ли пользователь карту."""
        if user_id not in self.current_games:
            return False, None, None
            
        game_state = self.current_games[user_id]
        selected_card = game_state["options"][selected_index]
        is_correct = selected_card['en'] == game_state["target_card"]['en']
        
        # Очищаем состояние игры
        if is_correct:
            del self.current_games[user_id]
            
        return is_correct, game_state["target_card"], selected_card

def get_try_again_keyboard() -> InlineKeyboardMarkup:
    """Возвращает клавиатуру для повторной попытки."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            "🎲 Попробовать еще раз",
            callback_data="try_again"
        ),
        InlineKeyboardButton(
            "🔙 Вернуться в меню",
            callback_data="return_to_menu"
        )
    )
    return keyboard 