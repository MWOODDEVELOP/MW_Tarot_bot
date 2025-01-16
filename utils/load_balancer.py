import asyncio
import logging
from typing import Dict, List, Optional
import aiohttp
from dataclasses import dataclass
import time
from .cluster_manager import ClusterManager

@dataclass
class RequestStats:
    total_requests: int = 0
    success_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_request_time: float = 0.0

class LoadBalancer:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoadBalancer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._cluster = ClusterManager()
            self._stats: Dict[str, RequestStats] = {}
            self._lock = asyncio.Lock()
            self._request_window = 60  # окно в секундах для сбора статистики
            self._initialized = True
            self._monitoring_task = None

    async def start_monitoring(self):
        """Запуск мониторинга нагрузки."""
        if not self._monitoring_task:
            self._monitoring_task = asyncio.create_task(self._monitor_load())

    async def stop_monitoring(self):
        """Остановка мониторинга нагрузки."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
            self._monitoring_task = None

    async def get_best_node(self, request_type: str) -> Optional[str]:
        """Получение наиболее подходящего узла для обработки запроса."""
        async with self._lock:
            available_nodes = [
                node_id for node_id, node in self._cluster.nodes.items()
                if node.is_alive
            ]
            
            if not available_nodes:
                return None
            
            # Учитываем статистику запросов и нагрузку узлов
            weighted_nodes = []
            for node_id in available_nodes:
                node = self._cluster.nodes[node_id]
                stats = self._stats.get(node_id, RequestStats())
                
                # Вычисляем вес узла
                success_rate = (stats.success_requests / stats.total_requests) if stats.total_requests > 0 else 1
                load_factor = 1 - (node.load / 100)  # Преобразуем загрузку в коэффициент (0-1)
                response_time_factor = 1 / (stats.average_response_time + 1)  # Избегаем деления на 0
                
                weight = (success_rate * 0.4 + load_factor * 0.4 + response_time_factor * 0.2)
                weighted_nodes.append((node_id, weight))
            
            # Выбираем узел с наибольшим весом
            return max(weighted_nodes, key=lambda x: x[1])[0]

    async def record_request(self, node_id: str, success: bool, response_time: float):
        """Запись статистики запроса."""
        async with self._lock:
            if node_id not in self._stats:
                self._stats[node_id] = RequestStats()
            
            stats = self._stats[node_id]
            stats.total_requests += 1
            if success:
                stats.success_requests += 1
            else:
                stats.failed_requests += 1
            
            # Обновляем среднее время ответа
            stats.average_response_time = (
                (stats.average_response_time * (stats.total_requests - 1) + response_time)
                / stats.total_requests
            )
            stats.last_request_time = time.time()

    async def _monitor_load(self):
        """Мониторинг нагрузки на узлы."""
        while True:
            try:
                current_time = time.time()
                async with self._lock:
                    # Очищаем устаревшую статистику
                    for node_id in list(self._stats.keys()):
                        stats = self._stats[node_id]
                        if current_time - stats.last_request_time > self._request_window:
                            self._stats[node_id] = RequestStats()
                
                # Проверяем необходимость перераспределения нагрузки
                await self._rebalance_if_needed()
                
                await asyncio.sleep(5)  # Проверка каждые 5 секунд
            except Exception as e:
                logging.error(f"Ошибка при мониторинге нагрузки: {e}")
                await asyncio.sleep(1)

    async def _rebalance_if_needed(self):
        """Проверка и перераспределение нагрузки при необходимости."""
        async with self._lock:
            active_nodes = [
                (node_id, node) for node_id, node in self._cluster.nodes.items()
                if node.is_alive
            ]
            
            if not active_nodes:
                return
            
            # Вычисляем среднюю нагрузку
            avg_load = sum(node.load for _, node in active_nodes) / len(active_nodes)
            
            # Находим перегруженные узлы
            overloaded_nodes = [
                (node_id, node) for node_id, node in active_nodes
                if node.load > avg_load * 1.2  # 20% выше средней нагрузки
            ]
            
            # Находим недогруженные узлы
            underloaded_nodes = [
                (node_id, node) for node_id, node in active_nodes
                if node.load < avg_load * 0.8  # 20% ниже средней нагрузки
            ]
            
            if overloaded_nodes and underloaded_nodes:
                # TODO: Реализовать логику миграции данных между узлами
                logging.info("Обнаружен дисбаланс нагрузки, требуется перераспределение")

    def get_load_stats(self) -> Dict:
        """Получение статистики нагрузки."""
        return {
            node_id: {
                "total_requests": stats.total_requests,
                "success_rate": (stats.success_requests / stats.total_requests * 100) if stats.total_requests > 0 else 0,
                "average_response_time": stats.average_response_time,
                "load": self._cluster.nodes[node_id].load if node_id in self._cluster.nodes else 0
            }
            for node_id, stats in self._stats.items()
        } 