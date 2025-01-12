🔮 MW Tarot Bot | Бот для гадания на картах Таро

[English](#english) | [Русский](#russian)

# English

A Telegram bot for Tarot card readings using the classic Rider-Waite deck. The bot offers personalized readings for different aspects of life: finances, relationships, career, and daily/weekly/monthly predictions.

## Key Features
- 78-card Rider-Waite Tarot deck
- Multiple reading themes (finances, relationships, career, etc.)
- Three-card spreads with detailed interpretations
- Historical context for each card
- Beautiful card imagery
- User-friendly interface with intuitive navigation
- Spread history saving for each user

# Russian

Telegram-бот для гадания на картах Таро с использованием классической колоды Райдера-Уэйта. Бот предлагает персональные предсказания для различных аспектов жизни: финансы, отношения, карьера, а также ежедневные, еженедельные и ежемесячные прогнозы.

## Основные возможности
- Полная колода Таро Райдера-Уэйта (78 карт)
- Различные темы для гадания (финансы, отношения, карьера и др.)
- Расклады из трёх карт с подробными толкованиями
- Историческая справка по каждой карте
- Красивые изображения карт
- Удобный интерфейс с интуитивной навигацией
- Сохранение истории раскладов для каждого пользователя

## 🌟 Описание
Телеграм-бот для гадания на картах Таро с различными тематическими раскладами. Бот предлагает:
- Различные тематики для гадания (финансы, отношения, карьера и др.)
- Расклад из трех карт
- Сохранение истории раскладов для каждого пользователя
- Подробные значения карт
- Поддержку изображений карт

## 📋 Требования
- Python 3.9+
- Git

## 💻 Как читать эту инструкцию

### Обозначения в документации

1. Блоки кода, обозначенные ```bash, нужно вводить в командную строку (терминал):
   - Windows: PowerShell или командная строка (CMD)
   - macOS: Terminal (Терминал)
   - Linux: Terminal (Терминал)

Пример блока кода:
```bash
python --version
```
Это означает, что вам нужно:
1. Открыть командную строку
2. Ввести команду `python --version`
3. Нажать Enter

### Как открыть командную строку

#### Windows:
1. Способ 1:
   - Нажмите Win + R
   - Введите `cmd` или `powershell`
   - Нажмите Enter

2. Способ 2:
   - Нажмите Win
   - Введите `PowerShell`
   - Нажмите Enter

#### macOS:
1. Способ 1:
   - Нажмите Command + Space
   - Введите `Terminal`
   - Нажмите Enter

2. Способ 2:
   - Откройте Finder
   - Перейдите в Applications → Utilities
   - Найдите Terminal

#### Linux:
1. Способ 1:
   - Нажмите Ctrl + Alt + T

2. Способ 2:
   - Откройте меню приложений
   - Найдите Terminal или Консоль

## 💻 Локальная установка и запуск

### Windows

1. Установка Python:
   - Скачайте Python 3.9+ с [официального сайта](https://www.python.org/downloads/)
   - При установке отметьте галочку "Add Python to PATH"
   - Проверьте установку:
   ```cmd
   python --version
   ```

2. Установка Git:
   - Скачайте Git с [официального сайта](https://git-scm.com/download/windows)
   - Установите с настройками по умолчанию
   - Проверьте установку:
   ```cmd
   git --version
   ```

3. Клонирование проекта:
   ```cmd
   git clone <URL вашего репозитория>
   cd <папка проекта>
   ```

4. Создание виртуального окружения:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

5. Установка зависимостей:
   ```cmd
   pip install -r requirements.txt
   ```

6. Настройка проекта:
   - Создайте папки для данных и изображений:
   ```cmd
   mkdir data
   mkdir images\tarot
   ```
   - Поместите `tarot_deck.json` в папку `data`
   - Поместите изображения карт в папку `images\tarot`

7. Запуск бота:
   ```cmd
   python bot.py
   ```

### macOS

1. Установка Homebrew (если не установлен):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Установка Python:
   ```bash
   brew install python@3.9
   python3 --version
   ```

3. Установка Git:
   ```bash
   brew install git
   git --version
   ```

4. Клонирование проекта:
   ```bash
   git clone <URL вашего репозитория>
   cd <папка проекта>
   ```

5. Создание виртуального окружения:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

6. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```

7. Настройка проекта:
   ```bash
   mkdir -p data images/tarot
   ```
   - Поместите `tarot_deck.json` в папку `data`
   - Поместите изображения карт в папку `images/tarot`

8. Запуск бота:
   ```bash
   python3 bot.py
   ```

### Linux (Ubuntu/Debian)

1. Установка Python и Git:
   ```bash
   sudo apt update
   sudo apt install -y python3.9 python3.9-venv python3-pip git
   ```

2. Проверка установки:
   ```bash
   python3 --version
   git --version
   ```

3. Клонирование проекта:
   ```bash
   git clone <URL вашего репозитория>
   cd <папка проекта>
   ```

4. Создание виртуального окружения:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Установка зависимостей:
   ```bash
   pip install -r requirements.txt
   ```

6. Настройка проекта:
   ```bash
   mkdir -p data images/tarot
   ```
   - Поместите `tarot_deck.json` в папку `data`
   - Поместите изображения карт в папку `images/tarot`

7. Запуск бота:
   ```bash
   python3 bot.py
   ```

## 🔄 Остановка бота
- Windows: Нажмите Ctrl+C в окне командной строки
- macOS/Linux: Нажмите Ctrl+C в терминале

## ⚠️ Устранение проблем

### Windows
- Если Python не найден: Проверьте переменную PATH в системных настройках
- Если pip не работает: Попробуйте `python -m pip install -r requirements.txt`
- Проблемы с правами: Запустите командную строку от имени администратора

### macOS
- Если python3 не найден после установки: Перезапустите терминал
- Проблемы с правами: Используйте `sudo` для команд, требующих прав администратора
- Проблемы с Homebrew: Выполните `brew doctor`

### Linux
- Проблемы с правами: Используйте `sudo` для команд, требующих прав администратора
- Если python3.9 не доступен в репозиториях:
  ```bash
  sudo add-apt-repository ppa:deadsnakes/ppa
  sudo apt update
  sudo apt install python3.9
  ```

## 🚀 Развертывание на сервере (для начинающих)

### Что такое развертывание?
Развертывание (деплой) - это процесс установки и запуска бота на удаленном сервере, чтобы он работал 24/7. 

### Что вам понадобится:
1. Сервер (VPS) с операционной системой Linux (Ubuntu/Debian)
   - Можно арендовать на площадках: DigitalOcean, Linode, VScale и др.
   - Рекомендуемые характеристики: 1GB RAM, 1 CPU
2. SSH-клиент для подключения к серверу
   - Windows: PuTTY или Windows Terminal
   - macOS/Linux: встроенный терминал
3. Доступ к серверу:
   - IP-адрес сервера
   - Логин (обычно root или ubuntu)
   - Пароль или SSH-ключ

### Пошаговое руководство по развертыванию

#### 1. Подключение к серверу

**Для Windows (через PuTTY):**
1. Скачайте и установите PuTTY
2. Введите IP-адрес сервера в поле "Host Name"
3. Нажмите "Open"
4. Введите логин и пароль

**Для Windows (через Terminal), macOS, Linux:**
```bash
ssh ваш_логин@ip_адрес_сервера
# Пример: ssh root@123.456.789.10
```

#### 2. Обновление системы
После подключения к серверу выполните:
```bash
# Обновление списка пакетов
sudo apt update

# Обновление установленных пакетов
sudo apt upgrade -y
```

#### 3. Установка необходимых программ
```bash
# Установка Docker
sudo apt install -y docker.io

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление вашего пользователя в группу docker (чтобы не писать sudo)
sudo usermod -aG docker $USER

# Применение изменений группы
newgrp docker
```

#### 4. Подготовка файлов бота

1. Клонирование проекта:
```bash
# Переход в домашнюю директорию
cd ~

# Клонирование репозитория
git clone <URL вашего репозитория>
cd <папка проекта>
```

2. Создание необходимых директорий:
```bash
# Создание директорий для данных и изображений
mkdir -p data images/tarot
```

3. Загрузка файлов на сервер:

**Для Windows (через WinSCP):**
1. Скачайте и установите WinSCP
2. Подключитесь к серверу, используя те же данные, что и для SSH
3. Перетащите файлы:
   - `tarot_deck.json` в папку `data/`
   - изображения карт (.jpg) в папку `images/tarot/`

**Для macOS/Linux (через терминал):**
```bash
# С локального компьютера выполните:
scp путь/к/tarot_deck.json ваш_логин@ip_адрес_сервера:~/папка_проекта/data/
scp путь/к/картам/*.jpg ваш_логин@ip_адрес_сервера:~/папка_проекта/images/tarot/
```

#### 5. Настройка и запуск бота

1. Проверка прав доступа:
```bash
# Установка правильных прав доступа
sudo chown -R $USER:$USER data/ images/
chmod -R 755 data/ images/
```

2. Запуск бота:
```bash
# Делаем скрипт запуска исполняемым
chmod +x start.sh

# Запускаем бота
./start.sh
```

#### 6. Проверка работы бота

1. Проверка статуса:
```bash
# Проверка, что контейнер запущен
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

2. Тестирование бота:
- Откройте Telegram
- Найдите вашего бота
- Отправьте команду `/start`
- Проверьте, что бот отвечает

### Часто встречающиеся проблемы

#### Бот не запускается
1. Проверьте логи:
```bash
docker-compose logs -f
```

2. Проверьте, что все файлы на месте:
```bash
# Проверка структуры директорий
ls -la

# Проверка файлов в data
ls -la data/

# Проверка изображений
ls -la images/tarot/
```

#### Проблемы с правами доступа
```bash
# Исправление прав доступа
sudo chown -R $USER:$USER .
chmod -R 755 .
```

#### Docker не запускается
```bash
# Проверка статуса Docker
sudo systemctl status docker

# Перезапуск Docker
sudo systemctl restart docker
```

### Полезные команды для управления ботом

#### Просмотр работы бота
```bash
# Просмотр логов в реальном времени
docker-compose logs -f

# Просмотр последних 100 строк логов
docker-compose logs --tail=100
```

#### Управление ботом
```bash
# Остановка бота
docker-compose down

# Перезапуск бота
docker-compose restart

# Обновление бота (после изменений в коде)
git pull
docker-compose up --build -d
```

#### Мониторинг ресурсов
```bash
# Просмотр использования ресурсов
docker stats

# Просмотр места на диске
df -h
```

### Советы по безопасности

1. Регулярно обновляйте систему:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Используйте сложные пароли

3. Не храните токены и пароли в публичных репозиториях

4. Регулярно проверяйте логи на наличие ошибок

### Создание резервных копий

1. Бэкап данных:
```bash
# Создание архива с данными
tar -czf backup_$(date +%Y%m%d).tar.gz data/ images/
```

2. Скачивание бэкапа на локальный компьютер:
```bash
# С локального компьютера:
scp ваш_логин@ip_адрес_сервера:~/папка_проекта/backup_*.tar.gz ./
```

## 🔧 Конфигурация

### Настройка временной зоны
В файле `docker-compose.yml` можно изменить временную зону:
```yaml
environment:
  - TZ=Europe/Moscow
```

### Настройка автоматического перезапуска
В файле `docker-compose.yml` параметр `restart: always` обеспечивает автоматический перезапуск бота при сбоях или перезагрузке сервера.

## 📝 Логи
Логи контейнера сохраняются и доступны через Docker. Для их просмотра используйте:
```bash
# Последние логи
docker-compose logs --tail=100

# Логи в реальном времени
docker-compose logs -f

# Логи с временными метками
docker-compose logs -t
```

## ⚠️ Устранение неполадок

### Проблемы с правами доступа
Если возникают проблемы с правами доступа к файлам:
```bash
sudo chown -R $USER:$USER data/ images/
```

### Проблемы с Docker
Если контейнер не запускается:
```bash
# Проверка статуса Docker
sudo systemctl status docker

# Перезапуск Docker
sudo systemctl restart docker
```

### Очистка неиспользуемых ресурсов
```bash
# Удаление неиспользуемых образов
docker image prune -a

# Удаление всех остановленных контейнеров
docker container prune
```

## Скачивание изображений карт

В проекте есть специальный скрипт `download_all_cards.py` для автоматического скачивания всех изображений карт Таро колоды Райдера-Уэйта. Скрипт скачивает все 78 карт:
- 22 карты Старших Арканов
- 56 карт Младших Арканов (4 масти по 14 карт)

Для запуска скрипта выполните:
```bash
python download_all_cards.py
```

Скрипт автоматически:
- Создаст директорию `images/tarot` если она не существует
- Скачает изображения всех карт из открытых источников
- Правильно назовет файлы в соответствии с форматом, который ожидает бот
- Пропустит уже существующие файлы
- Выведет информацию о процессе скачивания

После выполнения скрипта все изображения будут доступны в директории `images/tarot`. 