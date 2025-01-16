from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN
from handlers import register_handlers, set_monitor, register_feedback_handlers
import logging
import asyncio
from utils.daily_predictions import DailyPredictionManager
from utils.database import Database
from utils.user_manager import UserManager
from utils.card_manager import CardManager
from utils.monitoring import BotMonitor
from aiogram.types import Message
from functools import wraps
import time
import os
from pathlib import Path
from aiogram.contrib.fsm_storage.memory import MemoryStorage

def log_command(monitor):
    """Декоратор для логирования команд с измерением времени выполнения."""
    def decorator(func):
        @wraps(func)
        async def wrapper(update, *args, **kwargs):
            start_time = time.time()
            try:
                result = await func(update, *args, **kwargs)
                end_time = time.time()
                
                # Определяем тип обновления и получаем нужные данные
                if isinstance(update, types.CallbackQuery):
                    user_id = update.from_user.id
                    command = update.data
                else:  # Message
                    user_id = update.from_user.id
                    command = update.get_command() or update.text
                
                monitor.log_command(
                    user_id,
                    command,
                    True,
                    end_time - start_time
                )
                return result
            except Exception as e:
                end_time = time.time()
                
                # Определяем тип обновления для логирования ошибки
                if isinstance(update, types.CallbackQuery):
                    user_id = update.from_user.id
                    command = update.data
                else:  # Message
                    user_id = update.from_user.id
                    command = update.get_command() or update.text
                
                monitor.log_command(
                    user_id,
                    command,
                    False,
                    end_time - start_time
                )
                monitor.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    user_id=user_id
                )
                raise
        return wrapper
    return decorator

class BotManager:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.daily_prediction_manager = DailyPredictionManager(self.bot)
        self.db = Database()
        self._cleanup_tasks = []
        
        # Инициализируем монитор
        self.monitor = BotMonitor()
        
        # Устанавливаем глобальный монитор в handlers
        from handlers import set_monitor
        set_monitor(self.monitor)
    
    async def on_startup(self, dp: Dispatcher):
        """Действия при запуске бота."""
        self.monitor.logger.info("Запуск бота")
        
        # Инициализируем менеджеры
        self.user_manager = UserManager()
        self.card_manager = CardManager()
        
        # Инициализируем карты
        await self.card_manager.initialize()
        
        # Запускаем периодическую очистку кэша
        await self.user_manager.cache.start_cleanup()
        await self.card_manager.cache.start_cleanup()
        
        # Регистрируем хендлеры с декоратором логирования
        register_handlers(dp, log_command(self.monitor))
        
        # Проверяем наличие файлов обратной связи
        current_dir = Path(__file__).parent
        feedback_path = current_dir / "utils" / "feedback.py"
        handlers_path = current_dir / "handlers" / "feedback_handlers.py"
        
        if feedback_path.exists() and handlers_path.exists():
            try:
                register_feedback_handlers(dp)
                self.monitor.logger.info("Обработчики обратной связи зарегистрированы")
            except ImportError as e:
                self.monitor.logger.warning(f"Не удалось загрузить модуль обратной связи: {e}")
                self.monitor.logger.warning(f"Пути: feedback={feedback_path}, handlers={handlers_path}")
        else:
            self.monitor.logger.info(f"Модуль обратной связи отключен. Файлы не найдены: feedback={not feedback_path.exists()}, handlers={not handlers_path.exists()}")
        
        # Запускаем периодическую отправку предсказаний
        self._cleanup_tasks.append(
            asyncio.create_task(self.daily_prediction_manager.schedule_daily_predictions())
        )
        
        # Запускаем мониторинг ресурсов
        self._cleanup_tasks.append(
            asyncio.create_task(self.monitor.monitor_resources())
        )
    
    async def on_shutdown(self, dp: Dispatcher):
        """Действия при остановке бота."""
        self.monitor.logger.info("Остановка бота")
        
        # Останавливаем периодическую очистку кэша
        await self.user_manager.cache.stop_cleanup()
        await self.card_manager.cache.stop_cleanup()
        
        # Сохраняем финальную статистику
        await self.monitor.save_stats()
        
        # Отменяем все фоновые задачи
        for task in self._cleanup_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def run(self):
        """Запуск бота."""
        executor.start_polling(
            self.dp,
            skip_updates=True,
            on_startup=self.on_startup,
            on_shutdown=self.on_shutdown
        )

if __name__ == '__main__':
    bot_manager = BotManager()
    bot_manager.run() 