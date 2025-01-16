from fastapi import FastAPI, HTTPException
import uvicorn
from typing import Dict, Any, Optional
import asyncio
import logging
from .cluster_manager import ClusterManager
from .cache_manager import CacheManager
from pydantic import BaseModel

app = FastAPI()
cluster_manager = ClusterManager()
cache_manager = CacheManager()

class NodeRegistration(BaseModel):
    node_id: str
    host: str
    port: int

class CacheItem(BaseModel):
    value: Any
    ttl: Optional[int] = None

@app.post("/node/register")
async def register_node(node: NodeRegistration):
    """Регистрация нового узла в кластере."""
    success = await cluster_manager.register_node(node.node_id, node.host, node.port)
    if not success:
        raise HTTPException(status_code=400, detail="Node already registered")
    return {"status": "success"}

@app.post("/node/heartbeat/{node_id}")
async def update_heartbeat(node_id: str, stats: Dict[str, float]):
    """Обновление heartbeat от узла."""
    if node_id not in cluster_manager.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    
    node = cluster_manager.nodes[node_id]
    node.load = stats["load"]
    node.memory_usage = stats["memory_usage"]
    node.last_heartbeat = asyncio.get_event_loop().time()
    return {"status": "success"}

@app.get("/cache/{key}")
async def get_cache(key: str):
    """Получение значения из кэша."""
    value = await cache_manager.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"value": value}

@app.post("/cache/{key}")
async def set_cache(key: str, item: CacheItem):
    """Сохранение значения в кэш."""
    success = await cache_manager.set(key, item.value, item.ttl)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set cache")
    return {"status": "success"}

@app.delete("/cache/{key}")
async def delete_cache(key: str):
    """Удаление значения из кэша."""
    success = await cache_manager.delete(key)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"status": "success"}

@app.get("/stats")
async def get_stats():
    """Получение статистики узла."""
    return {
        "cluster": cluster_manager.get_cluster_stats(),
        "cache": cache_manager.get_stats()
    }

def start_node_api(host: str, port: int):
    """Запуск API узла."""
    uvicorn.run(app, host=host, port=port, log_level="info") 