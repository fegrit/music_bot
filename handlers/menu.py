from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from data import user_data

# Основное меню для пользователя
async def menu(update, context: CallbackContext):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    user_state = user_data.get_state(user_id)

    # Меню для разных состояний
    if user_state in ["awaiting_music_query", "in_recommendations"]:
        buttons = [["🚪 Выйти"]]  # Меню для режима рекомендаций или запроса музыки
    else:
        buttons = [  # Главное меню
            ["🔍 Найти музыку", "🎶 Получить рекомендации"],
            ["⚙️ Настройки", "ℹ️ О боте"]
        ]

    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    # Отправка сообщения с меню
    if update.message:
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# Обработчик для кнопки "Выйти"
async def handle_exit(update, context: CallbackContext):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id

    # Сброс состояния пользователя в "menu"
    user_data.set_state(user_id, "menu")
    await update.message.reply_text("Вы вышли из режима рекомендаций.")  # Сообщение для пользователя

    # Показать главное меню
    await menu(update, context)