from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from utils.feedback import FeedbackManager
import logging

# Инициализируем менеджер обратной связи
feedback_manager = FeedbackManager()

class FeedbackState(StatesGroup):
    waiting_for_type = State()
    waiting_for_message = State()

async def cmd_feedback(message: types.Message):
    """Начало процесса отправки обратной связи."""
    logging.info(f"Запущен процесс обратной связи пользователем {message.from_user.id}")
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🐞 Сообщить об ошибке", callback_data="feedback_bug"),
        types.InlineKeyboardButton("💡 Предложить идею", callback_data="feedback_suggestion")
    )
    await message.reply(
        "📝 *Обратная связь*\n\n"
        "Выберите тип обращения:",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def handle_feedback_type(callback: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа обратной связи."""
    feedback_type = callback.data.split('_')[1]
    await state.update_data(feedback_type=feedback_type)
    
    if feedback_type == "bug":
        text = (
            "🐞 *Сообщение об ошибке*\n\n"
            "Опишите, пожалуйста, проблему:\n"
            "- Что вы пытались сделать?\n"
            "- Что пошло не так?\n"
            "- Какой результат вы ожидали увидеть?"
        )
    else:
        text = (
            "💡 *Предложение*\n\n"
            "Опишите вашу идею или предложение по улучшению бота.\n"
            "Мы внимательно изучим каждое предложение!"
        )
    
    await callback.message.edit_text(
        text,
        parse_mode="Markdown"
    )
    await FeedbackState.waiting_for_message.set()

async def handle_feedback_message(message: types.Message, state: FSMContext):
    """Обработка текста обратной связи."""
    data = await state.get_data()
    feedback_type = data.get('feedback_type')
    
    success = await feedback_manager.add_feedback(
        message.from_user.id,
        feedback_type,
        message.text
    )
    
    if success:
        if feedback_type == "bug":
            response = "🐞 Спасибо за сообщение об ошибке! Мы обязательно рассмотрим проблему."
        else:
            response = "💡 Спасибо за предложение! Мы обязательно рассмотрим вашу идею."
    else:
        response = "❌ Извините, произошла ошибка при сохранении обратной связи. Попробуйте позже."
    
    await message.reply(response)
    await state.finish()

def register_feedback_handlers(dp):
    """Регистрация обработчиков обратной связи."""
    dp.register_message_handler(cmd_feedback, commands=['feedback'])
    dp.register_message_handler(cmd_feedback, lambda m: m.text == "📝 Обратная связь")
    dp.register_callback_query_handler(
        handle_feedback_type,
        lambda c: c.data.startswith('feedback_'),
        state="*"
    )
    dp.register_message_handler(
        handle_feedback_message,
        state=FeedbackState.waiting_for_message,
        content_types=types.ContentTypes.TEXT
    ) 