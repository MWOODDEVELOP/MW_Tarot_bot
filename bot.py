import json
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils import executor
from config import BOT_TOKEN
from handlers import register_handlers
from utils.card_manager import CardManager

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

def main():
    # Регистрация всех обработчиков
    register_handlers(dp)
    
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main() 