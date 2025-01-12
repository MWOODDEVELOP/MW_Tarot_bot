from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
import os
from config import IMAGES_PATH
from utils.card_manager import CardManager

# Хранение текущей информации пользователя
user_data = {}

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Финансы"), KeyboardButton("Отношения"))
    keyboard.add(KeyboardButton("Карта на сегодня"), KeyboardButton("Карьера"))
    keyboard.add(KeyboardButton("Карта на месяц"), KeyboardButton("Карта на неделю"))
    keyboard.add(KeyboardButton("Подсказка"))
    return keyboard

async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    
    # Создаем красивое приветственное сообщение
    welcome_text = (
        "🌟 *Добро пожаловать в магический мир Таро!* 🌟\n\n"
        "🔮 Я - ваш проводник в мир тайных знаний и древних предсказаний. "
        "Позвольте мне раскрыть перед вами завесу будущего и помочь найти ответы на ваши вопросы.\n\n"
        "✨ *Что я могу для вас сделать:*\n"
        "📈 *Финансы* - узнайте о своем финансовом будущем\n"
        "❤️ *Отношения* - получите совет в делах сердечных\n"
        "💼 *Карьера* - раскройте свой профессиональный потенциал\n"
        "🌅 *Карта на сегодня* - узнайте, что готовит для вас день\n"
        "🌙 *Карта на неделю* - загляните в ближайшее будущее\n"
        "🌟 *Карта на месяц* - откройте перспективы на месяц\n\n"
        "🎴 Для каждого расклада я выберу три карты, и вы сможете выбрать одну из них. "
        "Каждая карта несет в себе особое послание и мудрость веков.\n\n"
        "🔍 После каждого предсказания вы можете узнать историю выпавшей карты "
        "и глубже понять её значение.\n\n"
        "🌌 *Готовы начать своё магическое путешествие?*\n"
        "Выберите интересующую вас тему ниже 👇"
    )

    # Добавляем информацию о предыдущем раскладе, если он есть
    if CardManager.has_saved_spread(user_id):
        welcome_text += "\n\n🔮 У вас есть сохранённый расклад. Хотите его посмотреть? (Напишите 'да' или выберите новую тематику)"

    # Отправляем сообщение с форматированием Markdown
    await message.reply(welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def handle_theme(message: types.Message):
    user_id = str(message.from_user.id)
    theme = message.text
    
    # Генерируем расклад
    cards = CardManager.generate_spread()
    user_data[user_id] = {"theme": theme, "cards": cards}
    
    # Сохраняем расклад
    CardManager.save_spread(user_id, theme, cards)
    
    # Создаем красивые кнопки для выбора карт
    cards_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cards_keyboard.add(
        KeyboardButton("🎴 Карта ①"),
        KeyboardButton("🎴 Карта ②"),
        KeyboardButton("🎴 Карта ③")
    )
    
    await message.reply(
        "🔮 Карты Таро разложены перед вами...\n"
        "✨ Прислушайтесь к своей интуиции и выберите одну из трех карт:\n"
        "① - Первая карта\n"
        "② - Вторая карта\n"
        "③ - Третья карта",
        reply_markup=cards_keyboard
    )

async def handle_card_choice(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in user_data:
        await message.reply(
            "✨ Прежде чем выбрать карту, давайте определим тему для гадания.",
            reply_markup=get_main_keyboard()
        )
        return

    # Определяем номер выбранной карты из текста кнопки
    if "①" in message.text:
        chosen_index = 0
    elif "②" in message.text:
        chosen_index = 1
    else:
        chosen_index = 2

    card_info = CardManager.get_card_info(user_data[user_id]["cards"][chosen_index])
    
    if card_info is None:
        await message.reply(
            "Извините, произошла ошибка при получении информации о карте.",
            reply_markup=get_main_keyboard()
        )
        return
        
    theme = user_data[user_id]["theme"]
    user_data[user_id]["current_card"] = card_info

    # Формируем текст предсказания с предложениями
    prediction = card_info.get(theme, "Предсказание не найдено.")
    prediction_text = (
        f"🌟 Вы выбрали карту {card_info['ru']}...\n\n"
        f"✨ Вот что она говорит о вашем вопросе:\n\n"
        f"🔮 {prediction}\n\n"
        f"📜 Хотите узнать древнюю историю этой карты?\n"
        f"🔄 Или вернёмся к выбору новой темы?"
    )

    # Отправляем изображение карты вместе с текстом
    image_name = card_info['en'].replace('The ', '').replace(' ', '_')
    image_path = os.path.join(IMAGES_PATH, f"{image_name}.jpg")
    
    print(f"Trying to send image: {image_path}")
    print(f"Card info: {card_info}")
    print(f"File exists: {os.path.exists(image_path)}")
    
    # Создаем клавиатуру
    detail_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    detail_keyboard.add(KeyboardButton("Хочу узнать историю карты"))
    detail_keyboard.add(KeyboardButton("Вернуться к выбору тем"))
    
    if os.path.exists(image_path):
        try:
            await message.bot.send_photo(
                message.chat.id, 
                InputFile(image_path),
                caption=prediction_text,
                reply_markup=detail_keyboard
            )
            print("Image and text sent successfully")
        except Exception as e:
            print(f"Error sending image: {e}")
            await message.reply(
                "Извините, возникла проблема при отправке карты. " + prediction_text,
                reply_markup=detail_keyboard
            )
    else:
        print(f"Image file not found: {image_path}")
        await message.reply(
            "Извините, изображение карты не найдено.\n\n" + prediction_text,
            reply_markup=detail_keyboard
        )

async def handle_history_request(message: types.Message):
    user_id = str(message.from_user.id)
    if user_id not in user_data or "current_card" not in user_data[user_id]:
        await message.reply(
            "🌙 Простите, но магическая связь с картой потеряна. Давайте начнем новое гадание.",
            reply_markup=get_main_keyboard()
        )
        return

    card_info = user_data[user_id]["current_card"]
    history = card_info.get("history", "История этой карты окутана тайной...")
    
    # Отправляем историю и кнопку возврата
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Вернуться к выбору тем"))
    history_text = (
        f"📜 *История карты {card_info['ru']}*\n\n"
        f"✨ {history}\n\n"
        "🔮 Каждая карта Таро хранит в себе древнюю мудрость и силу..."
    )
    await message.reply(history_text, parse_mode="Markdown", reply_markup=keyboard)

async def handle_return_to_themes(message: types.Message):
    await message.reply(
        "🌟 К какой сфере жизни обратимся теперь?\n"
        "✨ Выберите тему, которая вас интересует:",
        reply_markup=get_main_keyboard()
    )

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(handle_theme, 
                              lambda message: message.text in ["Финансы", "Отношения", "Карта на сегодня",
                                                            "Карьера", "Карта на месяц", "Карта на неделю", "Подсказка"])
    dp.register_message_handler(handle_card_choice, 
                              lambda message: message.text in ["🎴 Карта ①", "🎴 Карта ②", "🎴 Карта ③"])
    dp.register_message_handler(handle_history_request, lambda message: message.text == "Хочу узнать историю карты")
    dp.register_message_handler(handle_return_to_themes, lambda message: message.text == "Вернуться к выбору тем") 