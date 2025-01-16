# 🔮 Мистический Мир Таро

Телеграм-бот для гадания на картах Таро с расширенными возможностями и интерактивными функциями.

## ✨ Возможности

### 🎴 Гадания
- Расклады по различным сферам жизни:
  - 💰 Финансы
  - ❤️ Отношения
  - 💼 Карьера
  - 🌅 Карта дня
  - 🌟 На неделю
  - 🌙 На месяц
  - 💫 Подсказка

### 👑 Админ-панель
- Управление картами Таро
- Редактирование описаний и значений
- Статистика использования
- Мониторинг нагрузки
- Управление пользователями

### 📊 Мониторинг и аналитика
- Отслеживание использования команд
- Мониторинг производительности
- Расширенная система логирования
- Health-check система
- Метрики использования ресурсов
- Статистика пользователей

### 💾 База данных и кэширование
- SQLite для хранения данных
- Кэширование изображений
- Оптимизация запросов
- Управление сессиями
- Резервное копирование

### 🔄 Масштабируемость
- Поддержка кластеризации
- Балансировка нагрузки
- Асинхронная обработка
- Очереди сообщений
- Горизонтальное масштабирование

### 📝 Обратная связь
- Система отзывов
- Оценка предсказаний
- Сбор пожеланий
- Отчеты об ошибках
- Аналитика отзывов

### 🎲 Игра "Угадай карту"
- Интерактивная игра для развития интуиции
- Изучение значений карт в игровой форме
- Возможность узнать историю каждой карты
- Статистика успешности

### ⚙️ Настройки
- 🌓 Выбор темы оформления (светлая/тёмная)
- 🖼 Настройка отображения карт (с изображениями/текстом)
- 🔔 Подписка на ежедневные предсказания
- 📝 Система обратной связи
- 🌍 Выбор языка интерфейса

## 🚀 Развертывание бота на сервере

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y \
    curl \
    wget \
    git \
    nano \
    htop \
    ufw

# Настройка файрвола
sudo ufw allow ssh
sudo ufw enable
```

### 2. Установка Docker и Docker Compose

```bash
# Установка Docker
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Установка бота

```bash
# Создание директории проекта
sudo mkdir -p /opt/mw_tarot_bot
cd /opt/mw_tarot_bot

# Создание необходимых директорий
mkdir -p logs/feedback
mkdir -p images/tarot
mkdir -p data

# Клонирование репозитория
git clone https://github.com/MWOODDEVELOP/MW_Tarot_bot.git .

# Настройка прав
sudo chown -R $USER:$USER /opt/mw_tarot_bot
sudo chmod -R 755 /opt/mw_tarot_bot
sudo chmod +x start.sh
```

### 4. Настройка окружения

1. Создайте файл `.env`:
```bash
nano .env
```

2. Добавьте необходимые переменные:
```env
BOT_TOKEN=your_bot_token_here  # Токен от @BotFather
```

### 5. Запуск бота

```bash
# Сборка и запуск
docker-compose build
docker-compose up -d

# Проверка статуса
docker ps
docker-compose logs -f
curl http://localhost:8080/health
```

### 6. Автозапуск и мониторинг

```bash
# Создание systemd сервиса
sudo nano /etc/systemd/system/tarot-bot.service

# Содержимое файла:
[Unit]
Description=Tarot Bot Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/mw_tarot_bot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target

# Активация сервиса
sudo systemctl enable tarot-bot
sudo systemctl start tarot-bot
```

## 📁 Структура проекта

```
├── bot.py                    # Основной файл бота
├── config.py                # Конфигурация
├── Dockerfile              # Конфигурация Docker
├── docker-compose.yml     # Docker Compose конфигурация
├── requirements.txt       # Зависимости
├── start.sh              # Скрипт запуска
├── health_check.py      # Проверка здоровья
├── .env                # Переменные окружения
├── data/
│   ├── tarot_deck.json   # База данных карт
│   └── database.sqlite  # SQLite база данных
├── logs/
│   ├── bot.log          # Основные логи
│   ├── errors.log      # Логи ошибок
│   ├── debug.log      # Отладочные логи
│   └── feedback/      # Обратная связь
├── images/
│   └── tarot/         # Изображения карт
├── utils/
│   ├── card_manager.py    # Управление картами
│   ├── user_manager.py    # Управление пользователями
│   ├── image_manager.py   # Управление изображениями
│   ├── cache_manager.py   # Управление кэшем
│   ├── monitoring.py      # Система мониторинга
│   ├── database.py       # Работа с базой данных
│   ├── admin_panel.py   # Админ-панель
│   ├── feedback.py     # Обработка обратной связи
│   └── daily_predictions.py # Ежедневные предсказания
├── admin/
│   ├── templates/     # Шаблоны админки
│   ├── static/       # Статические файлы
│   └── routes.py    # Маршруты админки
└── games/
    └── guess_card.py      # Игра "Угадай карту"
```

## 🔧 Технические особенности

- 🐳 Docker контейнеризация
- 🔄 Автоматический перезапуск
- 📊 Мониторинг здоровья
- 💾 Кэширование изображений
- 📝 Ротация логов
- 🔒 Безопасность:
  - Непривилегированный пользователь
  - Только необходимые разрешения
  - Защита от перезаписи изображений
- 📦 База данных:
  - SQLite для хранения данных
  - Миграции и бэкапы
  - Оптимизация запросов
- 🔄 Масштабируемость:
  - Поддержка кластеризации
  - Балансировка нагрузки
  - Асинхронная обработка
- 📊 Мониторинг:
  - Prometheus метрики
  - Grafana дашборды
  - Алертинг
- 👑 Администрирование:
  - Веб-интерфейс админки
  - Управление контентом
  - Мониторинг системы

## 📝 Лицензия

GNU General Public License v3.0

## 👥 Авторы

- [Moonly_Wood_Development](https://github.com/MWOODDEVELOP)

## 🤝 Вклад в проект

Мы приветствуем ваш вклад в развитие проекта! Пожалуйста, ознакомьтесь с `CONTRIBUTING.md` для получения информации о том, как можно помочь проекту. 