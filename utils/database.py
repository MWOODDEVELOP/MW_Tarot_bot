import sqlite3
import json
import logging
import asyncio
from typing import Optional, Dict, List, Any
from pathlib import Path

class Database:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._lock = asyncio.Lock()
            self.db_path = Path('data/tarot.db')
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._initialize_database()
            self._initialized = True

    def _initialize_database(self):
        """Инициализация базы данных и создание таблиц."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        spreads_today INTEGER DEFAULT 0,
                        last_spread_date TEXT,
                        theme TEXT DEFAULT 'light',
                        show_images BOOLEAN DEFAULT TRUE,
                        daily_prediction BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Создаем таблицу карт
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name_en TEXT NOT NULL,
                        name_ru TEXT NOT NULL,
                        meaning TEXT,
                        history TEXT,
                        finances TEXT,
                        relationships TEXT,
                        career TEXT,
                        daily TEXT,
                        weekly TEXT,
                        monthly TEXT,
                        hint TEXT,
                        UNIQUE(name_en)
                    )
                ''')
                
                # Создаем таблицу раскладов
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS spreads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        theme TEXT NOT NULL,
                        cards TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')
                
                # Создаем индексы
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_daily_prediction ON users(daily_prediction)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_spreads_user_date ON spreads(user_id, created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cards_names ON cards(name_en, name_ru)')
                
                conn.commit()
                logging.info("База данных успешно инициализирована")
                
        except Exception as e:
            logging.error(f"Ошибка при инициализации базы данных: {e}")
            raise

    async def migrate_data(self):
        """Миграция данных из JSON файлов в SQLite."""
        try:
            # Миграция данных пользователей
            users_path = Path('data/users.json')
            if users_path.exists():
                async with self._lock:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        with open(users_path) as f:
                            users_data = json.load(f)
                            for user_id, user_data in users_data.items():
                                cursor.execute('''
                                    INSERT OR REPLACE INTO users 
                                    (user_id, spreads_today, last_spread_date, theme, 
                                     show_images, daily_prediction)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                ''', (
                                    int(user_id),
                                    user_data.get('spreads_today', 0),
                                    user_data.get('last_spread_date', ''),
                                    user_data.get('theme', 'light'),
                                    user_data.get('show_images', True),
                                    user_data.get('daily_prediction', False)
                                ))
                        conn.commit()
                        logging.info("Данные пользователей успешно мигрированы")

            # Миграция данных карт
            cards_path = Path('data/tarot_deck.json')
            if cards_path.exists():
                async with self._lock:
                    with sqlite3.connect(self.db_path) as conn:
                        cursor = conn.cursor()
                        with open(cards_path, 'r', encoding='utf-8') as f:
                            deck_data = json.load(f)
                            
                            # Словарь соответствия русских названий английским
                            name_mapping = {
                                # Старшие арканы
                                "Шут": "The Fool",
                                "Маг": "The Magician",
                                "Верховная Жрица": "The High Priestess",
                                "Императрица": "The Empress",
                                "Император": "The Emperor",
                                "Иерофант": "The Hierophant",
                                "Влюбленные": "The Lovers",
                                "Колесница": "The Chariot",
                                "Сила": "Strength",
                                "Отшельник": "The Hermit",
                                "Колесо Фортуны": "Wheel of Fortune",
                                "Справедливость": "Justice",
                                "Повешенный": "The Hanged Man",
                                "Смерть": "Death",
                                "Умеренность": "Temperance",
                                "Дьявол": "The Devil",
                                "Башня": "The Tower",
                                "Звезда": "The Star",
                                "Луна": "The Moon",
                                "Солнце": "The Sun",
                                "Суд": "Judgement",
                                "Мир": "The World",
                            }
                            
                            # Обработка Старших арканов
                            for ru_name, card_data in deck_data["Старшие арканы"].items():
                                en_name = name_mapping.get(ru_name, ru_name)
                                cursor.execute('''
                                    INSERT OR REPLACE INTO cards 
                                    (name_en, name_ru, meaning, history, finances,
                                     relationships, career, daily, weekly, monthly, hint)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    en_name,
                                    ru_name,
                                    card_data.get('meaning', ''),
                                    card_data.get('history', ''),
                                    card_data.get('Финансы', ''),
                                    card_data.get('Отношения', ''),
                                    card_data.get('Карьера', ''),
                                    card_data.get('Карта на сегодня', ''),
                                    card_data.get('Карта на неделю', ''),
                                    card_data.get('Карта на месяц', ''),
                                    card_data.get('Подсказка', '')
                                ))
                            
                            # Обработка Младших арканов
                            for suit, cards in deck_data["Младшие арканы"].items():
                                for ru_name, card_data in cards.items():
                                    # Формируем английское название для младших арканов
                                    parts = ru_name.split()
                                    if len(parts) >= 2:
                                        rank = parts[0]
                                        rank_map = {
                                            "Туз": "Ace",
                                            "Двойка": "Two",
                                            "Тройка": "Three",
                                            "Четверка": "Four",
                                            "Пятерка": "Five",
                                            "Шестерка": "Six",
                                            "Семерка": "Seven",
                                            "Восьмерка": "Eight",
                                            "Девятка": "Nine",
                                            "Десятка": "Ten",
                                            "Паж": "Page",
                                            "Рыцарь": "Knight",
                                            "Королева": "Queen",
                                            "Король": "King"
                                        }
                                        suit_map = {
                                            "Жезлов": "Wands",
                                            "Кубков": "Cups",
                                            "Мечей": "Swords",
                                            "Пентаклей": "Pentacles"
                                        }
                                        en_rank = rank_map.get(rank, rank)
                                        en_suit = suit_map.get(parts[-1], parts[-1])
                                        en_name = f"{en_rank} of {en_suit}"
                                    else:
                                        en_name = ru_name

                                    cursor.execute('''
                                        INSERT OR REPLACE INTO cards 
                                        (name_en, name_ru, meaning, history, finances,
                                         relationships, career, daily, weekly, monthly, hint)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        en_name,
                                        ru_name,
                                        card_data.get('meaning', ''),
                                        card_data.get('history', ''),
                                        card_data.get('Финансы', ''),
                                        card_data.get('Отношения', ''),
                                        card_data.get('Карьера', ''),
                                        card_data.get('Карта на сегодня', ''),
                                        card_data.get('Карта на неделю', ''),
                                        card_data.get('Карта на месяц', ''),
                                        card_data.get('Подсказка', '')
                                    ))
                            
                        conn.commit()
                        logging.info("Данные карт успешно мигрированы")

        except Exception as e:
            logging.error(f"Ошибка при миграции данных: {e}")
            raise

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Получение данных пользователя."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                    row = cursor.fetchone()
                    if row:
                        return {
                            'user_id': row[0],
                            'spreads_today': row[1],
                            'last_spread_date': row[2],
                            'theme': row[3],
                            'show_images': bool(row[4]),
                            'daily_prediction': bool(row[5])
                        }
                    return None
        except Exception as e:
            logging.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
            return None

    async def update_user(self, user_id: int, **kwargs) -> bool:
        """Обновляет данные пользователя в базе данных."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Формируем SET часть запроса динамически
                    set_parts = []
                    values = []
                    for key, value in kwargs.items():
                        set_parts.append(f"{key} = ?")
                        values.append(value)
                    
                    if not set_parts:
                        return False
                    
                    # Проверяем существует ли пользователь
                    cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
                    user_exists = cursor.fetchone() is not None
                    
                    if user_exists:
                        # Обновляем существующего пользователя
                        query = f"""
                            UPDATE users 
                            SET {', '.join(set_parts)}
                            WHERE user_id = ?
                        """
                        values.append(user_id)
                        cursor.execute(query, values)
                    else:
                        # Создаем нового пользователя
                        columns = ['user_id'] + list(kwargs.keys())
                        placeholders = ['?'] * (len(kwargs) + 1)
                        query = f"""
                            INSERT INTO users ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                        """
                        cursor.execute(query, [user_id] + values)
                    
                    conn.commit()
                    return True
                    
        except Exception as e:
            logging.error(f"Ошибка при обновлении пользователя {user_id}: {e}")
            return False

    async def get_card(self, name_en: str) -> Optional[Dict]:
        """Получение информации о карте."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM cards WHERE name_en = ?', (name_en,))
                    row = cursor.fetchone()
                    if row:
                        return {
                            'en': row[1],
                            'ru': row[2],
                            'meaning': row[3],
                            'history': row[4],
                            'Финансы': row[5],
                            'Отношения': row[6],
                            'Карьера': row[7],
                            'Карта на сегодня': row[8],
                            'Карта на неделю': row[9],
                            'Карта на месяц': row[10],
                            'Подсказка': row[11]
                        }
                    return None
        except Exception as e:
            logging.error(f"Ошибка при получении карты {name_en}: {e}")
            return None

    async def get_daily_subscribers(self) -> List[int]:
        """Получение списка подписчиков на ежедневные предсказания."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT user_id FROM users WHERE daily_prediction = TRUE')
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Ошибка при получении списка подписчиков: {e}")
            return [] 

    async def save_spread(self, user_id: int, theme: str, cards: str) -> bool:
        """Сохранение расклада в базу данных."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO spreads (user_id, theme, cards)
                        VALUES (?, ?, ?)
                    ''', (user_id, theme, cards))
                    conn.commit()
                    return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении расклада: {e}")
            return False

    async def get_last_spread(self, user_id: int) -> Optional[Dict]:
        """Получение последнего расклада пользователя."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT theme, cards, created_at
                        FROM spreads
                        WHERE user_id = ?
                        ORDER BY created_at DESC
                        LIMIT 1
                    ''', (user_id,))
                    row = cursor.fetchone()
                    if row:
                        return {
                            'theme': row[0],
                            'cards': json.loads(row[1]),
                            'created_at': row[2]
                        }
                    return None
        except Exception as e:
            logging.error(f"Ошибка при получении последнего расклада: {e}")
            return None

    async def get_user_spreads(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получение истории раскладов пользователя."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT theme, cards, created_at
                        FROM spreads
                        WHERE user_id = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    ''', (user_id, limit))
                    return [{
                        'theme': row[0],
                        'cards': json.loads(row[1]),
                        'created_at': row[2]
                    } for row in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Ошибка при получении истории раскладов: {e}")
            return []

    async def get_stats(self) -> Dict:
        """Получение статистики использования бота."""
        try:
            async with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    stats = {}
                    
                    # Общее количество пользователей
                    cursor.execute('SELECT COUNT(*) FROM users')
                    stats['total_users'] = cursor.fetchone()[0]
                    
                    # Количество подписчиков на ежедневные предсказания
                    cursor.execute('SELECT COUNT(*) FROM users WHERE daily_prediction = TRUE')
                    stats['daily_subscribers'] = cursor.fetchone()[0]
                    
                    # Общее количество раскладов
                    cursor.execute('SELECT COUNT(*) FROM spreads')
                    stats['total_spreads'] = cursor.fetchone()[0]
                    
                    # Количество раскладов за последние 24 часа
                    cursor.execute('''
                        SELECT COUNT(*) FROM spreads 
                        WHERE created_at >= datetime('now', '-1 day')
                    ''')
                    stats['spreads_last_24h'] = cursor.fetchone()[0]
                    
                    # Популярные темы раскладов
                    cursor.execute('''
                        SELECT theme, COUNT(*) as count 
                        FROM spreads 
                        GROUP BY theme 
                        ORDER BY count DESC 
                        LIMIT 5
                    ''')
                    stats['popular_themes'] = dict(cursor.fetchall())
                    
                    return stats
        except Exception as e:
            logging.error(f"Ошибка при получении статистики: {e}")
            return {} 