import asyncio
from datetime import datetime, time, timedelta
import logging
from aiogram import Bot
from utils.user_manager import UserManager
from utils.card_manager import CardManager
from settings import settings

class DailyPredictionManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.user_manager = UserManager()
        self.card_manager = CardManager()
        self.is_running = False
    
    async def send_daily_predictions(self):
        subscribers = self.user_manager.get_daily_prediction_subscribers()
        logging.info(f"Отправка дневных предсказаний {len(subscribers)} подписчикам")
        
        for user_id in subscribers:
            try:
                user = self.user_manager.get_user(user_id)
                card = self.card_manager.get_random_card()
                
                message_text = (
                    "🌟 Ваше предсказание на сегодня:\n\n"
                    f"🎴 *{card['ru']}*\n\n"
                    f"✨ {card['Карта на сегодня']}\n\n"
                    "Хорошего вам дня! ✨"
                )
                
                if user["show_images"]:
                    image_path = f"{settings.IMAGES_PATH}{card['en']}.jpg"
                    try:
                        with open(image_path, 'rb') as photo:
                            await self.bot.send_photo(
                                user_id,
                                photo=photo,
                                caption=message_text,
                                parse_mode="Markdown"
                            )
                    except Exception as e:
                        logging.error(f"Ошибка при отправке изображения: {e}")
                        await self.bot.send_message(
                            user_id,
                            message_text,
                            parse_mode="Markdown"
                        )
                else:
                    await self.bot.send_message(
                        user_id,
                        message_text,
                        parse_mode="Markdown"
                    )
                    
                await asyncio.sleep(0.5)  # Небольшая задержка между отправками
                    
            except Exception as e:
                logging.error(f"Ошибка при отправке дневного предсказания пользователю {user_id}: {e}")
                continue
    
    async def schedule_daily_predictions(self):
        if self.is_running:
            return
            
        self.is_running = True
        logging.info("Запуск планировщика дневных предсказаний")
        
        while True:
            try:
                now = datetime.now()
                target_time = time(hour=8, minute=0)  # Отправка в 8:00 утра
                
                if now.time() > target_time:
                    # Если текущее время больше целевого, ждем до следующего дня
                    tomorrow = datetime.combine(now.date(), target_time) + timedelta(days=1)
                    seconds_until_target = (tomorrow - now).total_seconds()
                else:
                    # Если текущее время меньше целевого, ждем до целевого времени сегодня
                    target = datetime.combine(now.date(), target_time)
                    seconds_until_target = (target - now).total_seconds()
                
                logging.info(f"Ожидание {seconds_until_target} секунд до следующей отправки")
                await asyncio.sleep(seconds_until_target)
                
                await self.send_daily_predictions()
                
            except Exception as e:
                logging.error(f"Ошибка в планировщике: {e}")
                await asyncio.sleep(60)  # Ждем минуту перед повторной попыткой 