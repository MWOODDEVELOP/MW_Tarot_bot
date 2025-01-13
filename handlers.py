from aiogram import Dispatcher, types, Bot
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
import os
from config import IMAGES_PATH
from utils.card_manager import CardManager
from utils.user_manager import UserManager
import logging
from games.guess_card import GuessCardGame, get_try_again_keyboard

# Хранение текущей информации пользователя
user_data = {}
user_manager = UserManager()
# Хранение ID последних сообщений для каждого пользователя
last_messages = {}
guess_game = GuessCardGame()

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("💰 Финансы"),
        KeyboardButton("❤️ Отношения")
    )
    keyboard.add(
        KeyboardButton("🌅 Карта дня"),
        KeyboardButton("💼 Карьера")
    )
    keyboard.add(
        KeyboardButton("🌙 На месяц"),
        KeyboardButton("🌟 На неделю")
    )
    keyboard.add(
        KeyboardButton("💫 Подсказка"),
        KeyboardButton("⚙️ Настройки")
    )
    keyboard.add(
        KeyboardButton("🎲 Угадай карту")
    )
    return keyboard

async def delete_previous_messages(chat_id: int, user_message: types.Message):
    """Удаляет предыдущие сообщения в чате."""
    if chat_id in last_messages:
        try:
            # Удаляем предыдущее сообщение бота
            await user_message.bot.delete_message(chat_id, last_messages[chat_id]["bot"])
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение бота: {e}")
        
        try:
            # Удаляем предыдущее сообщение пользователя
            await user_message.bot.delete_message(chat_id, last_messages[chat_id]["user"])
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение пользователя: {e}")

async def delete_user_message(message: types.Message):
    """Немедленно удаляет сообщение пользователя."""
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение пользователя: {e}")

async def send_message_and_save_id(message: types.Message, text: str, reply_markup=None, parse_mode=None):
    """Отправляет сообщение и сохраняет его ID."""
    # Сначала удаляем предыдущее сообщение бота
    if message.chat.id in last_messages and "bot" in last_messages[message.chat.id]:
        try:
            await message.bot.delete_message(message.chat.id, last_messages[message.chat.id]["bot"])
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение бота: {e}")
    
    # Немедленно удаляем сообщение пользователя
    await delete_user_message(message)
    
    # Отправляем новое сообщение
    sent_message = await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
    
    # Сохраняем только ID сообщения бота
    last_messages[message.chat.id] = {
        "bot": sent_message.message_id
    }
    
    return sent_message

async def send_photo_and_save_id(message: types.Message, photo, caption: str = None, reply_markup=None, parse_mode=None):
    """Отправляет фото и сохраняет ID сообщения."""
    # Сначала удаляем предыдущее сообщение бота
    if message.chat.id in last_messages and "bot" in last_messages[message.chat.id]:
        try:
            await message.bot.delete_message(message.chat.id, last_messages[message.chat.id]["bot"])
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение бота: {e}")
    
    # Немедленно удаляем сообщение пользователя
    await delete_user_message(message)
    
    # Отправляем новое сообщение с фото
    sent_message = await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
    
    # Сохраняем только ID сообщения бота
    last_messages[message.chat.id] = {
        "bot": sent_message.message_id
    }
    
    return sent_message

async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    
    # Создаем красивое приветственное сообщение
    welcome_text = (
        "✨ *Добро пожаловать в Мистический Мир Таро!* ✨\n\n"
        "🔮 Я - ваш личный проводник в мир древних тайн и предсказаний. "
        "Позвольте мне приоткрыть завесу будущего и помочь найти ответы на ваши вопросы.\n\n"
        "🌟 *Мои возможности:*\n\n"
        "💰 *Финансы*\n└ Раскройте секреты вашего финансового процветания\n\n"
        "❤️ *Отношения*\n└ Найдите путь к гармонии в личной жизни\n\n"
        "💼 *Карьера*\n└ Откройте новые профессиональные горизонты\n\n"
        "🌅 *Карта дня*\n└ Узнайте, какие энергии окружают вас сегодня\n\n"
        "🌟 *На неделю*\n└ Загляните в ближайшее будущее\n\n"
        "🌙 *На месяц*\n└ Раскройте перспективы грядущего месяца\n\n"
        "✨ *Как это работает:*\n"
        "🎴 Для каждого расклада я выберу три особенные карты.\n"
        "🌟 Прислушайтесь к своей интуиции при выборе карты.\n"
        "📜 После расклада вы сможете узнать древнюю историю выбранной карты.\n\n"
        "🌌 *Готовы начать магическое путешествие?*\n"
        "└ Выберите интересующую вас сферу жизни ⬇️"
    )

    # Добавляем информацию о предыдущем раскладе, если он есть
    if CardManager.has_saved_spread(user_id):
        welcome_text += "\n\n🎴 У вас есть сохранённый расклад. Хотите его посмотреть? (Напишите 'да' или выберите новую тему)"

    await send_message_and_save_id(message, welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

async def handle_theme(message: types.Message):
    user_id = message.from_user.id
    # Убираем эмодзи из темы
    theme = message.text.split(' ', 1)[1] if ' ' in message.text else message.text
    
    if not user_manager.can_make_spread(user_id):
        await message.reply(
            "⚠️ *Лимит раскладов на сегодня достигнут*\n\n"
            "🌙 Карты Таро нуждаются в отдыхе, чтобы восстановить свою магическую силу.\n"
            "✨ Пожалуйста, возвращайтесь завтра для новых предсказаний.\n\n"
            "💫 _Если вам срочно нужен совет, обратитесь к администратору._",
            parse_mode="Markdown"
        )
        return
    
    # Преобразуем названия тем для соответствия с tarot_deck.json
    theme_mapping = {
        "💰 Финансы": "Финансы",
        "❤️ Отношения": "Отношения",
        "🌅 Карта дня": "Карта на сегодня",
        "💼 Карьера": "Карьера",
        "🌙 На месяц": "Карта на месяц",
        "🌟 На неделю": "Карта на неделю",
        "💫 Подсказка": "Подсказка"
    }
    
    actual_theme = theme_mapping.get(message.text, message.text)
    
    cards = CardManager.generate_spread()
    user_data[str(user_id)] = {"theme": actual_theme, "cards": cards}
    user_manager.increment_spreads(user_id)
    CardManager.save_spread(str(user_id), actual_theme, cards)
    
    cards_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cards_keyboard.add(
        KeyboardButton("🎴"),
        KeyboardButton("🎴"),
        KeyboardButton("🎴")
    )
    
    await send_message_and_save_id(
        message,
        "✨ *Карты Таро разложены перед вами* ✨\n\n"
        "🔮 Я разложила три карты для вашего вопроса.\n"
        "💫 Прислушайтесь к своей интуиции и выберите одну из карт...\n\n"
        "🌟 _Каждая карта несёт своё уникальное послание._",
        reply_markup=cards_keyboard,
        parse_mode="Markdown"
    )

def get_card_image_name(card_name: str) -> str:
    """Преобразует название карты в имя файла изображения."""
    # Словарь для преобразования чисел в слова
    numbers = {
        "Two": "two", "Three": "three", "Four": "four", "Five": "five",
        "Six": "six", "Seven": "seven", "Eight": "eight", "Nine": "nine",
        "Ten": "ten", "Ace": "ace", "Page": "page", "Knight": "knight",
        "Queen": "queen", "King": "king"
    }
    
    # Убираем "The " из названия
    name = card_name.replace("The ", "")
    
    # Разбиваем название на части
    parts = name.split()
    
    # Преобразуем числа в слова, если это необходимо
    if parts[0] in numbers:
        parts[0] = numbers[parts[0]]
    
    # Соединяем части с подчеркиванием
    name = "_".join(parts)
    
    # Логируем результат
    logging.info(f"Оригинальное название карты: {card_name}")
    logging.info(f"Сформированное имя файла: {name}")
    
    return name

async def handle_card_choice(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message.reply(
            "✨ *Магическая связь прервалась*\n\n"
            "🌙 Пожалуйста, начните новый расклад, выбрав интересующую вас сферу.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Определяем индекс выбранной карты по порядку нажатия
    cards = user_data[user_id]["cards"]
    theme = user_data[user_id]["theme"]
    
    # Получаем индекс карты из сообщения
    if "current_card_index" not in user_data[user_id]:
        user_data[user_id]["current_card_index"] = 0
    card_index = user_data[user_id]["current_card_index"]
    user_data[user_id]["current_card_index"] = (card_index + 1) % 3
    
    card_name = cards[card_index]
    card_info = CardManager.get_card_info(card_name)
    user_data[user_id]["current_card"] = card_info
    
    # Создаем клавиатуру для дополнительных действий
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        KeyboardButton("📜 История карты"),
        KeyboardButton("🔮 Новый расклад")
    )
    
    # Формируем сообщение с предсказанием
    message_text = (
        f"✨ *Ваше предсказание для сферы {theme}* ✨\n\n"
        f"🎴 *{card_info['ru']}*\n\n"
        f"📜 *Значение карты:*\n└ _{card_info[theme]}_\n\n"
        "🌟 *Дополнительные действия:*\n"
        "└ Узнать историю карты или сделать новый расклад"
    )
    
    # Отправляем сообщение с картой
    if user_manager.get_user(int(user_id))["show_images"]:
        image_name = get_card_image_name(card_info['en'])
        image_path = os.path.join(IMAGES_PATH, f"{image_name}.jpg")
        logging.info(f"Попытка отправить изображение: {image_path}")
        
        try:
            if os.path.exists(image_path):
                logging.info(f"Файл найден: {image_path}")
                with open(image_path, 'rb') as photo:
                    await send_photo_and_save_id(
                        message,
                        photo=photo,
                        caption=message_text,
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
            else:
                logging.warning(f"Файл не найден: {image_path}")
                await send_message_and_save_id(
                    message,
                    message_text + "\n\n⚠️ _Изображение карты временно недоступно_",
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")
            await send_message_and_save_id(
                message,
                message_text + "\n\n⚠️ _Не удалось отправить изображение карты_",
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    else:
        await send_message_and_save_id(
            message,
            message_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

async def handle_history_request(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in user_data or "current_card" not in user_data[user_id]:
        await message.reply(
            "✨ *Магическая связь с картой потеряна*\n\n"
            "🌙 Давайте начнем новое гадание, чтобы восстановить связь с картами Таро.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return

    card_info = user_data[user_id]["current_card"]
    history = card_info.get("history", "История этой карты окутана тайной...")
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("🔮 Новый расклад"))
    
    history_text = (
        f"📜 *История карты {card_info['ru']}* 📜\n\n"
        f"✨ _{history}_\n\n"
        "🌟 *Мудрость веков:*\n"
        "└ Каждая карта Таро хранит в себе древние знания и силу...\n\n"
        "🔮 Хотите сделать новый расклад?"
    )
    
    if user_manager.get_user(int(user_id))["show_images"]:
        image_name = get_card_image_name(card_info['en'])
        image_path = os.path.join(IMAGES_PATH, f"{image_name}.jpg")
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await send_photo_and_save_id(
                    message,
                    photo=photo,
                    caption=history_text,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
                return
    
    await send_message_and_save_id(
        message,
        history_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_return_to_themes(message: types.Message):
    """Обработчик для возврата к выбору темы гадания."""
    await send_message_and_save_id(
        message,
        "✨ *Выберите сферу для нового предсказания* ✨\n\n"
        "🌟 Карты Таро готовы раскрыть перед вами новые тайны...\n"
        "└ Какая сфера жизни интересует вас сейчас?",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

async def settings_menu(message: types.Message):
    user = user_manager.get_user(message.from_user.id)
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            f"{'🌞' if user['theme'] == 'light' else '🌙'} Тема: {'Светлая' if user['theme'] == 'light' else 'Тёмная'}",
            callback_data="toggle_theme"
        ),
        InlineKeyboardButton(
            f"{'🖼' if user['show_images'] else '📝'} Карты: {'С изображениями' if user['show_images'] else 'Текстом'}",
            callback_data="toggle_images"
        ),
        InlineKeyboardButton(
            f"{'🔔' if user['daily_prediction'] else '🔕'} Предсказание дня: {'Включено' if user['daily_prediction'] else 'Отключено'}",
            callback_data="toggle_daily"
        )
    )
    
    await send_message_and_save_id(
        message,
        "⚙️ *Настройки вашего магического пространства*\n\n"
        "✨ Здесь вы можете настроить:\n\n"
        "🌓 *Тема оформления*\n└ Выберите комфортный для вас стиль\n\n"
        "🖼 *Изображения карт*\n└ Показывать карты с иллюстрациями или текстом\n\n"
        "🔮 *Предсказание дня*\n└ Получайте ежедневные карты и их толкования\n\n"
        "_Нажмите на кнопки ниже для изменения настроек_",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_settings_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = user_manager.get_user(user_id)
    
    if callback.data == "toggle_theme":
        new_theme = "dark" if user["theme"] == "light" else "light"
        user_manager.update_preferences(user_id, theme=new_theme)
        await callback.answer(
            f"✨ Тема изменена на {'тёмную 🌙' if new_theme == 'dark' else 'светлую 🌞'}"
        )
    
    elif callback.data == "toggle_images":
        new_show_images = not user["show_images"]
        user_manager.update_preferences(user_id, show_images=new_show_images)
        await callback.answer(
            f"🎴 Карты будут показываться {'с изображениями' if new_show_images else 'текстом'}"
        )
    
    elif callback.data == "toggle_daily":
        is_subscribed = user_manager.toggle_daily_prediction(user_id)
        await callback.answer(
            f"{'🔔 Вы подписались на' if is_subscribed else '🔕 Вы отписались от'} ежедневные предсказания"
        )
    
    # Обновляем клавиатуру
    keyboard = InlineKeyboardMarkup(row_width=1)
    user = user_manager.get_user(user_id)
    
    keyboard.add(
        InlineKeyboardButton(
            f"{'🌞' if user['theme'] == 'light' else '🌙'} Тема: {'Светлая' if user['theme'] == 'light' else 'Тёмная'}",
            callback_data="toggle_theme"
        ),
        InlineKeyboardButton(
            f"{'🖼' if user['show_images'] else '📝'} Карты: {'С изображениями' if user['show_images'] else 'Текстом'}",
            callback_data="toggle_images"
        ),
        InlineKeyboardButton(
            f"{'🔔' if user['daily_prediction'] else '🔕'} Предсказание дня: {'Включено' if user['daily_prediction'] else 'Отключено'}",
            callback_data="toggle_daily"
        )
    )
    
    # Обновляем сообщение с настройками
    settings_text = (
        "⚙️ *Настройки вашего магического пространства*\n\n"
        "✨ Здесь вы можете настроить:\n\n"
        "🌓 *Тема оформления*\n└ Выберите комфортный для вас стиль\n\n"
        "🖼 *Изображения карт*\n└ Показывать карты с иллюстрациями или текстом\n\n"
        "🔮 *Предсказание дня*\n└ Получайте ежедневные карты и их толкования\n\n"
        "_Нажмите на кнопки ниже для изменения настроек_"
    )
    
    # Обновляем сообщение бота
    edited_message = await callback.message.edit_text(
        settings_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    # Сохраняем только ID сообщения бота
    last_messages[callback.message.chat.id] = {
        "bot": edited_message.message_id
    }

async def send_daily_prediction(bot: Bot):
    subscribers = user_manager.get_daily_prediction_subscribers()
    card_manager = CardManager()
    
    for user_id in subscribers:
        try:
            user = user_manager.get_user(user_id)
            card = card_manager.get_random_card()
            
            message_text = (
                "✨ *Ваше Предсказание на Сегодня* ✨\n\n"
                f"🎴 Карта дня: *{card['ru']}*\n\n"
                f"📜 Послание карты:\n└ _{card['Карта на сегодня']}_\n\n"
                "🌟 Пусть этот день принесёт вам мудрость и озарение!\n"
                "└ _Ваш мистический проводник_"
            )
            
            # Удаляем предыдущее сообщение бота, если оно есть
            if user_id in last_messages and "bot" in last_messages[user_id]:
                try:
                    await bot.delete_message(user_id, last_messages[user_id]["bot"])
                except Exception as e:
                    logging.warning(f"Не удалось удалить предыдущее предсказание: {e}")
            
            # Отправляем новое предсказание
            if user["show_images"]:
                image_name = get_card_image_name(card['en'])
                image_path = os.path.join(IMAGES_PATH, f"{image_name}.jpg")
                if os.path.exists(image_path):
                    sent_message = await bot.send_photo(
                        user_id,
                        photo=InputFile(image_path),
                        caption=message_text,
                        parse_mode="Markdown"
                    )
                else:
                    sent_message = await bot.send_message(
                        user_id,
                        message_text,
                        parse_mode="Markdown"
                    )
            else:
                sent_message = await bot.send_message(
                    user_id,
                    message_text,
                    parse_mode="Markdown"
                )
            
            # Сохраняем только ID сообщения бота
            last_messages[user_id] = {
                "bot": sent_message.message_id
            }
                
        except Exception as e:
            logging.error(f"Ошибка при отправке дневного предсказания пользователю {user_id}: {e}")
            continue

async def handle_guess_card_game(message: types.Message):
    """Начинает новую игру 'Угадай карту'."""
    target_card, options, keyboard = guess_game.start_new_game(message.from_user.id)
    
    # Логируем информацию о карте
    logging.info(f"Загаданная карта: {target_card}")
    
    # Формируем сообщение
    game_text = (
        "🎲 *Игра: Угадай карту* 🎲\n\n"
        f"✨ Я загадала карту *{target_card['ru']}*\n\n"
        "🎴 Перед вами 5 перевёрнутых карт\n"
        "└ Найдите загаданную карту среди них!\n\n"
        "💫 Прислушайтесь к своей интуиции..."
    )
    
    # Отправляем изображение загаданной карты
    image_name = get_card_image_name(target_card['en'])
    image_path = os.path.join(IMAGES_PATH, f"{image_name}.jpg")
    
    # Логируем путь к файлу
    logging.info(f"Путь к изображению: {image_path}")
    logging.info(f"Файл существует: {os.path.exists(image_path)}")
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as photo:
            await send_photo_and_save_id(
                message,
                photo=photo,
                caption=game_text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
    else:
        await send_message_and_save_id(
            message,
            game_text + "\n\n⚠️ _Изображение карты временно недоступно_",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

async def handle_guess_callback(callback: types.CallbackQuery):
    """Обрабатывает выбор карты в игре."""
    # Получаем индекс выбранной карты
    data_parts = callback.data.split('_')
    selected_index = int(data_parts[1])
    
    # Проверяем угадал ли пользователь
    is_correct, target_card, selected_card = guess_game.check_guess(callback.from_user.id, selected_index)
    
    # Удаляем сообщение с кнопками
    await callback.message.delete()
    
    if is_correct:
        success_text = (
            "🎉 *Поздравляем! Вы угадали!* 🎉\n\n"
            "✨ Ваша интуиция привела вас к правильной карте!\n\n"
            "🌟 История этой карты:\n"
            f"└ _{target_card.get('history', 'История этой карты окутана тайной...')}_\n\n"
            "💫 Продолжайте развивать свой дар..."
        )
        
        # Используем функцию для отправки сообщения с сохранением ID
        await send_message_and_save_id(
            callback.message,
            success_text,
            parse_mode="Markdown",
            reply_markup=get_try_again_keyboard()
        )
    else:
        fail_text = (
            "✨ *К сожалению, это не та карта* ✨\n\n"
            f"🎴 Вы выбрали: *{selected_card['ru']}*\n"
            f"└ _{selected_card.get('history', 'История этой карты окутана тайной...')}_\n\n"
            "💫 Не отчаивайтесь, каждая попытка приближает вас\n"
            "к лучшему пониманию карт Таро...\n"
            "└ Попробуете еще раз?"
        )
        
        # Отправляем сообщение с изображением выбранной карты
        selected_image = get_card_image_name(selected_card['en'])
        selected_path = os.path.join(IMAGES_PATH, f"{selected_image}.jpg")
        
        if os.path.exists(selected_path):
            with open(selected_path, 'rb') as photo:
                await send_photo_and_save_id(
                    callback.message,
                    photo=photo,
                    caption=fail_text,
                    parse_mode="Markdown",
                    reply_markup=get_try_again_keyboard()
                )
        else:
            await send_message_and_save_id(
                callback.message,
                fail_text,
                parse_mode="Markdown",
                reply_markup=get_try_again_keyboard()
            )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(settings_menu, lambda m: m.text == "⚙️ Настройки")
    dp.register_message_handler(handle_theme, 
                              lambda message: any(message.text.endswith(theme) for theme in 
                              ["💰 Финансы", "❤️ Отношения", "🌅 Карта дня", "💼 Карьера", 
                               "🌙 На месяц", "🌟 На неделю", "💫 Подсказка"]))
    dp.register_message_handler(handle_card_choice, 
                              lambda message: message.text == "🎴")
    dp.register_message_handler(handle_history_request, lambda message: message.text == "📜 История карты")
    dp.register_message_handler(handle_return_to_themes, lambda message: message.text in ["🔮 Новый расклад", "🔮 Вернуться к гаданию"])
    dp.register_callback_query_handler(handle_settings_callback, lambda c: c.data.startswith("toggle_"))
    # Добавляем обработчики для игры
    dp.register_message_handler(handle_guess_card_game, lambda m: m.text == "🎲 Угадай карту")
    dp.register_message_handler(handle_guess_card_game, lambda m: m.text == "🎲 Попробовать еще раз")
    dp.register_callback_query_handler(handle_guess_callback, lambda c: c.data.startswith("guess_")) 