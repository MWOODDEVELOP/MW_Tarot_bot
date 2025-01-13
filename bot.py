from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import logging
from settings import settings
from handlers import register_handlers
from utils.daily_predictions import DailyPredictionManager

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация хендлеров
register_handlers(dp)

# Инициализация менеджера ежедневных предсказаний
daily_predictions = DailyPredictionManager(bot)

async def on_startup(dp):
    # Запуск планировщика ежедневных предсказаний
    asyncio.create_task(daily_predictions.schedule_daily_predictions())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup) 