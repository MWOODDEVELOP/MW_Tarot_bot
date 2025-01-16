import asyncio
import logging
from typing import Dict, List, Optional
import json
import aiohttp
from dataclasses import dataclass
import psutil
import time

@dataclass
class NodeInfo:
    id: str
    host: str
    port: int
    load: float
    memory_usage: float
    is_alive: bool = True
    last_heartbeat: float = 0

class ClusterManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ClusterManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.nodes: Dict[str, NodeInfo] = {}
            self._master_node = True
            self._node_id = "node_1"
            self._host = None
            self._port = None
            self._lock = asyncio.Lock()
            self._heartbeat_interval = 5
            self._node_timeout = 15
            self._initialized = True
            self._cleanup_task = None
            self._heartbeat_task = None

    async def start(self, host: str, port: int, master: bool = True):
        """Запуск узла кластера."""
        self._master_node = master
        self._host = host
        self._port = port
        
        # Регистрируем себя
        await self.register_node(self._node_id, host, port)
        
        if not master:
            # Регистрируемся у мастер-узла
            await self._register_with_master()
        
        # Запускаем задачи мониторинга
        self._heartbeat_task = asyncio.create_task(self._send_heartbeat())
        if master:
            self._cleanup_task = asyncio.create_task(self._cleanup_dead_nodes())

    async def _register_with_master(self):
        """Регистрация у мастер-узла."""
        master_host = "localhost"  # В реальном приложении нужно настроить
        master_port = 8000
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{master_host}:{master_port}/node/register",
                    json={
                        "node_id": self._node_id,
                        "host": self._host,
                        "port": self._port
                    }
                ) as response:
                    if response.status != 200:
                        logging.error("Не удалось зарегистрироваться у мастер-узла")
        except Exception as e:
            logging.error(f"Ошибка при регистрации у мастер-узла: {e}")

    async def register_node(self, node_id: str, host: str, port: int) -> bool:
        """Регистрация нового узла в кластере."""
        async with self._lock:
            if node_id not in self.nodes:
                self.nodes[node_id] = NodeInfo(
                    id=node_id,
                    host=host,
                    port=port,
                    load=psutil.cpu_percent(),
                    memory_usage=psutil.virtual_memory().percent,
                    last_heartbeat=time.time()
                )
                logging.info(f"Зарегистрирован новый узел: {node_id}")
                return True
            return False

    async def get_best_node(self) -> Optional[NodeInfo]:
        """Получение узла с наименьшей нагрузкой."""
        async with self._lock:
            available_nodes = [node for node in self.nodes.values() if node.is_alive]
            if not available_nodes:
                return None
            return min(available_nodes, key=lambda x: (x.load, x.memory_usage))

    async def _send_heartbeat(self):
        """Отправка сигнала активности."""
        while True:
            try:
                current_load = psutil.cpu_percent()
                memory_usage = psutil.virtual_memory().percent
                current_time = time.time()
                
                # Обновляем свою информацию
                async with self._lock:
                    if self._node_id in self.nodes:
                        self.nodes[self._node_id].load = current_load
                        self.nodes[self._node_id].memory_usage = memory_usage
                        self.nodes[self._node_id].last_heartbeat = current_time
                
                # Отправляем heartbeat другим узлам
                if not self._master_node:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(
                                f"http://localhost:8000/node/heartbeat/{self._node_id}",
                                json={
                                    "load": current_load,
                                    "memory_usage": memory_usage
                                }
                            ) as response:
                                if response.status != 200:
                                    logging.warning("Не удалось отправить heartbeat")
                    except Exception as e:
                        logging.error(f"Ошибка при отправке heartbeat: {e}")
                
                await asyncio.sleep(self._heartbeat_interval)
            except Exception as e:
                logging.error(f"Ошибка в процессе heartbeat: {e}")
                await asyncio.sleep(1)

    async def _cleanup_dead_nodes(self):
        """Очистка неактивных узлов."""
        while True:
            try:
                current_time = time.time()
                async with self._lock:
                    dead_nodes = [
                        node_id for node_id, node in self.nodes.items()
                        if current_time - node.last_heartbeat > self._node_timeout
                    ]
                    for node_id in dead_nodes:
                        if node_id != self._node_id:  # Не помечаем себя как мертвый узел
                            self.nodes[node_id].is_alive = False
                            logging.warning(f"Узел {node_id} помечен как неактивный")
                
                await asyncio.sleep(self._node_timeout)
            except Exception as e:
                logging.error(f"Ошибка при очистке мертвых узлов: {e}")
                await asyncio.sleep(1)

    def get_cluster_stats(self) -> Dict:
        """Получение статистики кластера."""
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": len([n for n in self.nodes.values() if n.is_alive]),
            "average_load": sum(n.load for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0,
            "nodes": [
                {
                    "id": n.id,
                    "host": n.host,
                    "port": n.port,
                    "load": n.load,
                    "memory_usage": n.memory_usage,
                    "is_alive": n.is_alive,
                    "last_heartbeat": n.last_heartbeat
                } for n in self.nodes.values()
            ]
        }

    async def stop(self):
        """Остановка менеджера кластера."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass 