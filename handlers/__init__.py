"""
Инициализация обработчиков бота.
"""

# Словарь для хранения последних сообщений
last_messages = {}

# Глобальная переменная для хранения монитора
bot_monitor = None

def set_monitor(monitor):
    """Установка глобального монитора."""
    global bot_monitor
    bot_monitor = monitor

from .handlers import (
    register_handlers,
    delete_previous_messages,
    send_message_and_save_id,
    get_main_keyboard
)

from .feedback_handlers import register_feedback_handlers

__all__ = [
    'register_handlers',
    'set_monitor',
    'last_messages',
    'delete_previous_messages',
    'send_message_and_save_id',
    'get_main_keyboard',
    'bot_monitor',
    'register_feedback_handlers'
] 