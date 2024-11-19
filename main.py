from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from handlers import start, menu, settings, recommendations, about, music_search
from genre_pagination import handle_show_all_genres, handle_genre_navigation
from data.config import TELEGRAM_TOKEN
from data import user_data
from telegram import ReplyKeyboardMarkup

# Универсальный обработчик меню
async def menu_handler(update, context):
    user_id = update.message.from_user.id
    user_state = user_data.get_state(user_id)

    text = update.message.text
    print(f"Получено сообщение: {text}, состояние пользователя: {user_state}")

    # Команда "Выйти"
    if text == "🚪 Выйти":
        user_data.set_state(user_id, "menu")  # Сбрасываем состояние в меню
        # Возвращаем главное меню
        default_menu = ReplyKeyboardMarkup(
            [["🔍 Найти музыку", "🎶 Получить рекомендации"], ["⚙️ Настройки", "ℹ️ О боте"]],
            resize_keyboard=True
        )
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=default_menu)
        return

    # Обработка состояния "awaiting_genres"
    if user_state == "awaiting_genres":
        await settings.handle_genre_input(update, context)
        return

    # Обработка состояния "awaiting_music_query"
    if user_state == "awaiting_music_query":
        print("Передача управления в handle_music_search")
        await music_search.handle_music_search(update, context)
        return

    # Основные команды меню
    if text == "🔍 Найти музыку":
        user_data.set_state(user_id, "awaiting_music_query")
        await music_search.find_music(update, context)
    elif text == "🎶 Получить рекомендации":
        user_data.set_state(user_id, "in_recommendations")
        # Меню с кнопкой "Выйти"
        exit_menu = ReplyKeyboardMarkup([["🚪 Выйти"]], resize_keyboard=True)
        await update.message.reply_text("Загружаем рекомендации...", reply_markup=exit_menu)
        await recommendations.get_recommendation(update, context)
    elif text == "⚙️ Настройки":
        await settings.show_settings(update, context)
    elif text == "ℹ️ О боте":
        await about.about_bot(update, context)
    elif text == "Изменить жанры":
        await settings.change_genres(update, context)
    elif text == "Назад в меню":
        user_data.set_state(user_id, "menu")
        await menu.menu(update, context)

# Универсальный обработчик нажатий на кнопки
async def callback_query_handler(update, context):
    query = update.callback_query
    data = query.data
    print(f"Получен callback_data: {data}")

    if data == "exit":  # Обработка команды "Выйти" через inline-кнопку
        user_id = query.from_user.id
        user_data.set_state(user_id, "menu")  # Сбрасываем состояние
        print(f"Состояние пользователя {user_id} сброшено в menu")
        await query.answer()  # Подтверждаем нажатие
        await query.message.reply_text("Вы вернулись в главное меню.")
        await menu.menu(update, context)
        return
    elif data in ["like", "dislike"]:  # Оценка треков
        await recommendations.handle_like_dislike(update, context)
    elif data in ["spotify", "continue"]:  # Работа с треками
        await recommendations.send_track_link(update, context)
    elif data.startswith("show_all_genres"):  # Показать все жанры
        await handle_show_all_genres(update, context)
    elif data.startswith("show_genres_"):  # Навигация по жанрам
        await handle_genre_navigation(update, context)

# Основной запуск бота
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start.start))  # Стартовая команда
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))  # Меню
    application.add_handler(CallbackQueryHandler(callback_query_handler))  # Inline-кнопки

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()