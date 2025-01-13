#!/bin/bash

# Запуск health check сервера в фоновом режиме
python health_check.py &

# Запуск основного бота
exec python bot.py 