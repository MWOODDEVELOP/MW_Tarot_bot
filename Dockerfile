FROM python:3.9-slim

WORKDIR /app

# Установка необходимых системных пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY requirements.txt .
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Создание необходимых директорий
RUN mkdir -p data images

CMD ["python", "bot.py"] 