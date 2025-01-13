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

### 🎲 Игра "Угадай карту"
- Интерактивная игра для развития интуиции
- Изучение значений карт в игровой форме
- Возможность узнать историю каждой карты

### ⚙️ Настройки
- 🌓 Выбор темы оформления (светлая/тёмная)
- 🖼 Настройка отображения карт (с изображениями/текстом)
- 🔔 Подписка на ежедневные предсказания

## 🚀 Развертывание бота на сервере

### 1. Подготовка сервера

1. Подключитесь к вашему серверу через SSH:
```bash
ssh username@your_server_ip
```

2. Обновите систему:
```bash
sudo apt update && sudo apt upgrade -y
```

3. Установите Docker:
```bash
# Установка необходимых пакетов
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавление официального GPG-ключа Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновление списка пакетов
sudo apt update

# Установка Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Добавление вашего пользователя в группу docker
sudo usermod -aG docker $USER
```

4. Установите Docker Compose:
```bash
# Скачивание последней версии
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Установка прав на выполнение
sudo chmod +x /usr/local/bin/docker-compose
```

5. Перезагрузите систему или выполните новый вход:
```bash
sudo reboot
```

### 2. Установка бота

1. Создайте директорию для бота:
```bash
mkdir ~/tarot-bot
cd ~/tarot-bot
```

2. Клонируйте репозиторий:
```bash
git clone https://github.com/MWOODDEVELOP/tarot-bot.git .
```

3. Создайте файл `.env`:
```bash
nano .env
```

4. Добавьте в файл `.env` следующие строки:
```env
BOT_TOKEN=your_bot_token_here  # Замените на ваш токен от @BotFather
ADMIN_IDS=[123456789]          # Замените на ваш ID в Telegram
```

### 3. Запуск бота

1. Соберите и запустите контейнер:
```bash
docker-compose up -d --build
```

2. Проверьте, что бот запущен:
```bash
docker-compose ps
```

3. Посмотрите логи:
```bash
docker-compose logs -f
```

### 4. Управление ботом

#### Основные команды

- Остановка бота:
```bash
docker-compose down
```

- Перезапуск бота:
```bash
docker-compose restart
```

- Просмотр статуса:
```bash
docker-compose ps
```

#### Обновление бота

1. Остановите бота:
```bash
docker-compose down
```

2. Получите последние обновления:
```bash
git pull
```

3. Пересоберите и запустите контейнер:
```bash
docker-compose up -d --build
```

#### Просмотр логов

- Просмотр всех логов:
```bash
docker-compose logs
```

- Просмотр логов в реальном времени:
```bash
docker-compose logs -f
```

- Просмотр последних N строк:
```bash
docker-compose logs --tail=100
```

### 5. Резервное копирование

1. Создайте бэкап данных:
```bash
# Создайте директорию для бэкапов
mkdir -p ~/backups

# Скопируйте данные
cp -r data/ ~/backups/data_$(date +%Y%m%d)
```

2. Восстановление из бэкапа:
```bash
# Остановите бота
docker-compose down

# Восстановите данные
cp -r ~/backups/data_YYYYMMDD/* data/

# Запустите бота
docker-compose up -d
```

### 6. Устранение проблем

1. Если бот не запускается:
```bash
# Проверьте логи
docker-compose logs

# Проверьте статус контейнера
docker-compose ps

# Перезапустите с пересборкой
docker-compose up -d --build --force-recreate
```

2. Если проблемы с правами доступа:
```bash
# Установите правильные права на директории
sudo chown -R $USER:$USER ~/tarot-bot
```

3. Если нужно очистить все данные и начать заново:
```bash
# Остановите все контейнеры
docker-compose down

# Удалите все образы
docker system prune -a

# Запустите заново
docker-compose up -d --build
```

## 📁 Структура проекта

```
├── bot.py                 # Основной файл бота
├── config.py             # Конфигурация и настройки
├── requirements.txt      # Зависимости проекта
├── .env                 # Переменные окружения (не включен в репозиторий)
├── data/
│   ├── tarot_deck.json  # База данных карт
│   └── users.json       # Данные пользователей
├── images/              # Изображения карт
├── utils/
│   ├── card_manager.py  # Управление картами
│   └── user_manager.py  # Управление пользователями
└── games/
    └── guess_card.py    # Логика игры "Угадай карту"
```

## 📝 Лицензия

GNU General Public License v3.0. Этот проект защищен лицензией GPLv3, которая требует, чтобы все производные работы также распространялись под той же лицензией и запрещает использование кода в закрытых коммерческих продуктах. См. файл `LICENSE` для подробностей.

## 👥 Авторы

- [Moonly_Wood_Development](https://github.com/MWOODDEVELOP)

## 🤝 Вклад в проект

Мы приветствуем ваш вклад в развитие проекта! Пожалуйста, ознакомьтесь с `CONTRIBUTING.md` для получения информации о том, как можно помочь проекту. 