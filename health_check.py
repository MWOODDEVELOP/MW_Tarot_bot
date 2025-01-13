from aiohttp import web
import psutil
import os
import logging
from datetime import datetime

routes = web.RouteTableDef()

@routes.get('/health')
async def health_check(request):
    try:
        # Проверка использования памяти
        memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        
        # Проверка доступа к директориям
        dirs_to_check = [
            '/app/logs',
            '/app/images/tarot',
            '/app/data'
        ]
        
        all_dirs_accessible = all(os.access(d, os.R_OK | os.W_OK) for d in dirs_to_check)
        
        # Проверка наличия файла с картами
        cards_file_exists = os.path.exists('/app/data/tarot_deck.json')
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'memory_usage_mb': round(memory, 2),
            'directories_accessible': all_dirs_accessible,
            'cards_file_exists': cards_file_exists
        }
        
        return web.json_response(health_status)
    except Exception as e:
        logging.error(f"Health check failed: {str(e)}")
        return web.json_response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, port=8080) 