import logging
import asyncio
from datetime import datetime, date
from typing import Dict, List, Optional
from .database import Database
from .cache_manager import CacheManager

class UserManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self.db = Database()
            self.cache = CacheManager()
            self._initialized = True
            # Устанавливаем TTL для кэша пользователей (30 минут)
            self.cache.set_default_ttl(1800)

    async def get_user(self, user_id: int) -> Dict:
        """Получение информации о пользователе."""
        try:
            # Пробуем получить из кэша
            cache_key = f"user_{user_id}"
            user = await self.cache.get(cache_key)
            if user:
                logging.info(f"Получены данные пользователя {user_id} из кэша: {user}")
                return user

            # Если нет в кэше, получаем из базы
            user = await self.db.get_user(user_id)
            if not user:
                # Создаем нового пользователя с дефолтными настройками
                default_user = {
                    "theme": "light",
                    "show_images": True,
                    "daily_prediction": False,
                    "spreads_today": 0,
                    "last_spread_date": None
                }
                logging.info(f"Создан новый пользователь {user_id} с настройками: {default_user}")
                # Сохраняем в базу данных
                success = await self.db.update_user(user_id=user_id, **default_user)
                if success:
                    user = default_user
                else:
                    logging.error(f"Не удалось создать пользователя {user_id} в базе данных")
                    return default_user
            
            logging.info(f"Получены данные пользователя {user_id} из БД: {user}")
            
            # Сохраняем в кэш
            await self.cache.set(cache_key, user)
            return user
            
        except Exception as e:
            logging.error(f"Ошибка при получении пользователя {user_id}: {e}")
            # Возвращаем дефолтные настройки в случае ошибки
            return {
                "theme": "light",
                "show_images": True,
                "daily_prediction": False,
                "spreads_today": 0,
                "last_spread_date": None
            }

    async def can_make_spread(self, user_id: int) -> bool:
        """Проверка возможности сделать расклад."""
        user = await self.get_user(user_id)
        today = date.today().isoformat()
        
        if user['last_spread_date'] != today:
            # Сбрасываем счетчик в начале нового дня
            await self.update_user(user_id, spreads_today=0, last_spread_date=today)
            return True
            
        return user['spreads_today'] < 3  # Максимум 3 расклада в день

    async def increment_spreads(self, user_id: int) -> None:
        """Увеличение счетчика раскладов."""
        user = await self.get_user(user_id)
        today = date.today().isoformat()
        
        if user['last_spread_date'] != today:
            # Новый день - сбрасываем счетчик
            await self.update_user(
                user_id,
                spreads_today=1,
                last_spread_date=today
            )
        else:
            # Увеличиваем счетчик
            await self.update_user(
                user_id,
                spreads_today=user['spreads_today'] + 1
            )

    async def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновление настроек пользователя."""
        try:
            # Обновляем в базе данных
            success = await self.db.update_user(user_id, **kwargs)
            if success:
                # Обновляем кэш
                cache_key = f"user_{user_id}"
                user = await self.get_user(user_id)
                await self.cache.set(cache_key, user)
                
                # Если изменился статус подписки на рассылку, обновляем кэш подписчиков
                if 'daily_prediction' in kwargs:
                    await self.cache.delete('daily_subscribers')
            return success
        except Exception as e:
            logging.error(f"Ошибка при обновлении пользователя {user_id}: {e}")
            return False

    async def toggle_daily_prediction(self, user_id: int) -> bool:
        """Включение/выключение ежедневных предсказаний."""
        user = await self.get_user(user_id)
        new_state = not user['daily_prediction']
        success = await self.update_user(user_id, daily_prediction=new_state)
        return new_state if success else user['daily_prediction']

    async def get_daily_prediction_subscribers(self) -> List[int]:
        """Получение списка подписчиков на ежедневные предсказания."""
        try:
            # Пробуем получить из кэша
            subscribers = await self.cache.get('daily_subscribers')
            if subscribers is not None:
                return subscribers

            # Если нет в кэше, получаем из базы
            subscribers = await self.db.get_daily_subscribers()
            
            # Сохраняем в кэш на 5 минут
            await self.cache.set('daily_subscribers', subscribers, ttl=300)
            return subscribers
            
        except Exception as e:
            logging.error(f"Ошибка при получении списка подписчиков: {e}")
            return [] 

    async def update_preferences(self, user_id: int, **preferences):
        """Обновляет настройки пользователя."""
        try:
            logging.info(f"Начало обновления настроек для пользователя {user_id}: {preferences}")
            
            # Получаем текущие настройки
            current_user = await self.get_user(user_id)
            logging.info(f"Текущие настройки пользователя {user_id}: {current_user}")
            
            # Обновляем только допустимые настройки
            valid_preferences = {
                k: v for k, v in preferences.items() 
                if k in ['theme', 'show_images', 'daily_prediction']
            }
            logging.info(f"Валидные настройки для обновления: {valid_preferences}")
            
            if not valid_preferences:
                logging.warning(f"Нет допустимых настроек для обновления у пользователя {user_id}")
                return current_user
            
            # Обновляем в базе данных
            success = await self.db.update_user(user_id, **valid_preferences)
            logging.info(f"Результат обновления в БД: {'успешно' if success else 'ошибка'}")
            
            if success:
                # Обновляем текущие настройки
                updated_user = dict(current_user)
                updated_user.update(valid_preferences)
                
                # Обновляем кэш
                cache_key = f"user_{user_id}"
                await self.cache.set(cache_key, updated_user)
                logging.info(f"Кэш обновлен для пользователя {user_id}: {updated_user}")
                
                # Если изменился статус подписки на рассылку, обновляем кэш подписчиков
                if 'daily_prediction' in valid_preferences:
                    await self.cache.delete('daily_subscribers')
                    logging.info("Кэш подписчиков очищен")
                
                return updated_user
            else:
                logging.error(f"Не удалось обновить настройки в БД для пользователя {user_id}")
                return current_user
            
        except Exception as e:
            logging.error(f"Ошибка при обновлении настроек пользователя {user_id}: {e}")
            return await self.get_user(user_id)  # Возвращаем текущие настройки в случае ошибки

    async def reset_preferences(self, user_id: int):
        """Сбрасывает настройки пользователя к значениям по умолчанию."""
        default_preferences = {
            'theme': 'light',
            'show_images': True,
            'daily_prediction': False
        }
        
        return await self.update_preferences(user_id, **default_preferences) 