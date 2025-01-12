#!/bin/bash

# Обновляем код из репозитория, если есть
git pull

# Останавливаем старые контейнеры
docker-compose down

# Собираем и запускаем новые
docker-compose up --build -d

# Выводим логи
docker-compose logs -f 