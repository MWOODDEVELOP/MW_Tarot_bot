import logging
import time
from typing import Dict, Any, Optional
import asyncio
import psutil
import gc
import json
import aiohttp
from .cluster_manager import ClusterManager

class CacheManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cache = {}
            self._timestamps = {}
            self._max_memory_percent = 75
            self._cleanup_threshold = 1000
            self._default_ttl = 3600
            self._lock = asyncio.Lock()
            self._initialized = True
            self._cleanup_task = None
            self._cluster = ClusterManager()
            self._partition_count = 100  # Количество партиций для шардинга
    
    def _get_partition(self, key: str) -> int:
        """Определение партиции для ключа."""
        return hash(key) % self._partition_count
    
    async def _get_node_for_key(self, key: str) -> Optional[str]:
        """Получение узла для ключа на основе консистентного хэширования."""
        partition = self._get_partition(key)
        best_node = await self._cluster.get_best_node()
        return best_node.id if best_node else None
    
    async def get(self, key: str) -> Optional[Any]:
        """Получение значения из распределенного кэша."""
        try:
            node_id = await self._get_node_for_key(key)
            if not node_id:
                return None
            
            if node_id == self._cluster._node_id:
                async with self._lock:
                    if key not in self._cache:
                        return None
                    
                    if time.time() - self._timestamps[key] > self._default_ttl:
                        del self._cache[key]
                        del self._timestamps[key]
                        return None
                    
                    return self._cache[key]
            else:
                # Получение значения с другого узла
                node = self._cluster.nodes.get(node_id)
                if not node or not node.is_alive:
                    return None
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://{node.host}:{node.port}/cache/{key}") as response:
                        if response.status == 200:
                            return await response.json()
                        return None
        except Exception as e:
            logging.error(f"Ошибка при получении из кэша: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Сохранение значения в распределенный кэш."""
        try:
            node_id = await self._get_node_for_key(key)
            if not node_id:
                return False
            
            if node_id == self._cluster._node_id:
                async with self._lock:
                    if self._check_memory_usage():
                        await self._cleanup_cache()
                    
                    self._cache[key] = value
                    self._timestamps[key] = time.time()
                    
                    if len(self._cache) > self._cleanup_threshold:
                        await self._cleanup_cache()
                    
                    return True
            else:
                # Сохранение значения на другом узле
                node = self._cluster.nodes.get(node_id)
                if not node or not node.is_alive:
                    return False
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"http://{node.host}:{node.port}/cache/{key}",
                        json={"value": value, "ttl": ttl}
                    ) as response:
                        return response.status == 200
        except Exception as e:
            logging.error(f"Ошибка при сохранении в кэш: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удаление значения из распределенного кэша."""
        try:
            node_id = await self._get_node_for_key(key)
            if not node_id:
                return False
            
            if node_id == self._cluster._node_id:
                async with self._lock:
                    if key in self._cache:
                        del self._cache[key]
                        del self._timestamps[key]
                        return True
                    return False
            else:
                node = self._cluster.nodes.get(node_id)
                if not node or not node.is_alive:
                    return False
                
                async with aiohttp.ClientSession() as session:
                    async with session.delete(f"http://{node.host}:{node.port}/cache/{key}") as response:
                        return response.status == 200
        except Exception as e:
            logging.error(f"Ошибка при удалении из кэша: {e}")
            return False
    
    async def clear(self) -> None:
        """Полная очистка кэша."""
        async with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            gc.collect()  # Принудительный сбор мусора
    
    def _check_memory_usage(self) -> bool:
        """Проверка использования памяти."""
        memory = psutil.Process().memory_percent()
        return memory > self._max_memory_percent
    
    async def _cleanup_cache(self) -> None:
        """Очистка устаревших записей."""
        current_time = time.time()
        keys_to_delete = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > self._default_ttl
        ]
        
        for key in keys_to_delete:
            await self.delete(key)
        
        if keys_to_delete:
            gc.collect()
    
    async def _periodic_cleanup(self) -> None:
        """Периодическая очистка кэша."""
        while True:
            await asyncio.sleep(300)  # Проверка каждые 5 минут
            await self._cleanup_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша."""
        return {
            "total_items": len(self._cache),
            "memory_usage": psutil.Process().memory_percent(),
            "cache_age": {
                key: time.time() - timestamp
                for key, timestamp in self._timestamps.items()
            }
        }
    
    async def prefetch(self, keys: list, fetch_func) -> None:
        """Предварительная загрузка данных в кэш."""
        for key in keys:
            if not await self.get(key):
                value = await fetch_func(key)
                if value:
                    await self.set(key, value)
    
    def set_max_memory_percent(self, percent: int) -> None:
        """Установка максимального процента использования памяти."""
        if 0 < percent < 100:
            self._max_memory_percent = percent
    
    def set_cleanup_threshold(self, threshold: int) -> None:
        """Установка порога для очистки кэша."""
        if threshold > 0:
            self._cleanup_threshold = threshold
    
    def set_default_ttl(self, ttl: int) -> None:
        """Установка времени жизни кэша по умолчанию."""
        if ttl > 0:
            self._default_ttl = ttl 
    
    async def start_cleanup(self):
        """Запуск периодической очистки кэша."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def stop_cleanup(self):
        """Остановка периодической очистки кэша."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None 