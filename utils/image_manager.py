from typing import Optional, Dict, Union
from PIL import Image
import io
import os
import asyncio
import aiofiles
import logging
from config import IMAGES_PATH
import time
from pathlib import Path

class ImageManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self._cache = {}
            self._cache_lifetime = 3600  # 1 час
            self._max_cache_size = 100
            self._last_cleanup = time.time()
            self._cleanup_interval = 3600  # 1 час
            self._cleanup_task = None
            self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images', 'tarot')
            logging.info(f"Найдено {len(os.listdir(self.base_path))} файлов в директории {self.base_path}")
            self._initialized = True
            self._preload_common_images()

    async def start_cleanup(self):
        """Запуск задачи очистки кэша."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def get_image(self, image_name: str) -> Optional[bytes]:
        image_name = image_name.replace("The ", "").replace(" ", "_")
        if not image_name.endswith('.jpg'):
            image_name = f"{image_name}.jpg"
            
        if image_name in self._cache:
            cache_time, image_data = self._cache[image_name]
            if time.time() - cache_time < self._cache_lifetime:
                return image_data
            
        image_data = await self._optimize_image(image_name)
        if image_data:
            self._cache[image_name] = (time.time(), image_data)
            if len(self._cache) > self._max_cache_size:
                await self._cleanup_cache()
        return image_data

    async def _optimize_image(self, image_path: str) -> Optional[bytes]:
        try:
            base_name = os.path.basename(image_path)
            base_name = base_name.replace("The ", "").replace(" ", "_")
            full_path = os.path.join(self.base_path, base_name)
            
            if not os.path.exists(full_path):
                logging.error(f"Файл не найден: {full_path}")
                return None
                
            async with aiofiles.open(full_path, 'rb') as f:
                image_data = await f.read()
            
            image = Image.open(io.BytesIO(image_data))
            # Оптимизация изображения
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        except Exception as e:
            logging.error(f"Ошибка при оптимизации изображения {image_path}: {e}")
            return None

    def _preload_common_images(self):
        """Предварительная загрузка часто используемых изображений."""
        self._common_cards = [
            "Fool", "Magician", "High_Priestess",
            "Empress", "Emperor", "Hierophant"
        ]

    async def preload_images(self):
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith('.jpg'):
                    # Убираем расширение .jpg и обрабатываем имя
                    card_name = filename[:-4]  # Убираем расширение .jpg
                    card_name = card_name.replace("The_", "").replace("_", " ")
                    await self.get_image(card_name)
        except Exception as e:
            logging.error(f"Ошибка при предзагрузке изображений: {e}")
            logging.error(f"Текущая директория: {self.base_path}")
            logging.error(f"Доступные файлы: {os.listdir(self.base_path)}")

    async def _periodic_cleanup(self):
        """Периодическая очистка устаревших изображений из кэша."""
        while True:
            try:
                current_time = time.time()
                # Создаем список ключей для удаления
                to_remove = [
                    path for path, (timestamp, _) in self._cache.items()
                    if current_time - timestamp > self._cache_lifetime
                ]
                
                # Удаляем устаревшие изображения
                for path in to_remove:
                    del self._cache[path]
                
                # Ждем час перед следующей проверкой
                await asyncio.sleep(3600)
            except Exception as e:
                logging.error(f"Ошибка при очистке кэша: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке

    def clear_cache(self):
        """Принудительная очистка всего кэша."""
        self._cache.clear()

    def get_cache_stats(self) -> dict:
        """Получение статистики кэша."""
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self._max_cache_size,
            "cache_lifetime": self._cache_lifetime,
            "cached_images": list(self._cache.keys())
        } 