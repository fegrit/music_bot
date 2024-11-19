# settings.py

import json
from data import user_data
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

# Загрузка словаря переводов жанров
with open("data/genre_translations.json", "r", encoding="utf-8") as f:
    GENRE_TRANSLATION = json.load(f)

EXIT_COMMANDS = {"назад в меню", "отмена", "⚙️ настройки"}

# Отображение текущих настроек пользователя
async def show_settings(update, context):
    user_id = update.message.from_user.id
    user_genres = user_data.get_user_genres(user_id)

    if user_genres:
        translated_genres = [GENRE_TRANSLATION.get(genre, genre) for genre in user_genres]
        genres_text = ", ".join(translated_genres)
        message = f"Ваши текущие жанры: {genres_text}\n\nВы можете изменить их, выбрав опцию ниже."
    else:
        message = "У вас пока нет выбранных жанров. Вы можете выбрать их сейчас."

    keyboard = [["Изменить жанры", "Назад в меню"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(message, reply_markup=reply_markup)

# Обработка команды изменения жанров
async def change_genres(update, context):
    user_id = update.message.from_user.id
    user_data.set_state(user_id, "awaiting_genres")  # Устанавливаем состояние ожидания выбора жанров
    print(f"Установлено состояние 'awaiting_genres' для пользователя {user_id}")

    message = (
        "Пожалуйста, выберите до четырех новых жанров для обновления ваших предпочтений.\n"
        "Нажмите 'Показать все жанры' для выбора из полного списка."
    )

    keyboard = [[InlineKeyboardButton("Показать все жанры", callback_data="show_all_genres")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup)

# Обработка ввода жанров
async def handle_genre_input(update, context):
    user_id = update.message.from_user.id
    input_text = update.message.text.strip().lower()

    # Проверка на команду выхода
    if input_text in EXIT_COMMANDS:
        user_data.set_state(user_id, "menu")
        await update.message.reply_text("Вы вернулись в главное меню.")
        return

    # Проверяем состояние перед обработкой жанров
    if user_data.get_state(user_id) == "awaiting_genres":
        selected_genres = [genre.strip() for genre in input_text.split(",")]

        # Проверка количества выбранных жанров
        if not 1 <= len(selected_genres) <= 4:
            await update.message.reply_text("Пожалуйста, выберите от одного до четырех жанров, разделив их запятой.")
            return

        # Допустимые варианты для жанров r&b и k-pop
        rnb_variants = {"r&b", "rnb", "арнби", "рнб", "р-б", "эрэнби", "эрнби"}
        kpop_variants = {"k-pop", "kpop", "кейпоп", "к-поп", "к поп", "кпоп"}

        # Нормализация жанров
        normalized_genres = [
            GENRE_TRANSLATION.get("r-n-b") if genre in rnb_variants else 
            GENRE_TRANSLATION.get("k-pop") if genre in kpop_variants else 
            GENRE_TRANSLATION.get(genre, genre)
            for genre in selected_genres
        ]
        print(f"Жанры после нормализации: {normalized_genres}")

        # Проверка на допустимые жанры
        valid_genres_rus = set(GENRE_TRANSLATION.values())
        unrecognized_genres = [genre for genre in normalized_genres if genre not in valid_genres_rus]
        
        if unrecognized_genres:
            await update.message.reply_text(
                f"Следующие жанры не распознаны: {', '.join(unrecognized_genres)}.\n"
                "Пожалуйста, выберите жанры из списка и введите их через запятую."
            )
            return

        # Перевод жанров для сохранения
        translated_genres = [next((k for k, v in GENRE_TRANSLATION.items() if v == genre), genre) for genre in normalized_genres]
        
        # Обновляем и сохраняем жанры
        user_data.user_states[str(user_id)]["genres"] = translated_genres
        user_data.set_state(user_id, "menu")
        user_data.save_user_data()

        updated_genres_text = ", ".join([genre.capitalize() for genre in normalized_genres])
        await update.message.reply_text(f"Ваши жанры обновлены на: {updated_genres_text}.")