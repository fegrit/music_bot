from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import math
import json

# Загрузка переводов жанров из JSON-файла
with open("data/genre_translations.json", "r", encoding="utf-8") as f:
    GENRE_TRANSLATION = json.load(f)

# Количество жанров на одной странице
GENRES_PER_PAGE = 10

# Функция для отображения страницы с жанрами
async def show_genres_page(update, context, page=0):
    user_id = update.effective_user.id
    genres_list = list(GENRE_TRANSLATION.values())  # Все жанры на русском
    total_pages = math.ceil(len(genres_list) / GENRES_PER_PAGE)
    
    # Определение начального и конечного индексов для текущей страницы
    start = page * GENRES_PER_PAGE
    end = start + GENRES_PER_PAGE
    genres_text = "\n".join(genres_list[start:end])

    # Текст сообщения
    message_text = f"Доступные жанры (стр. {page + 1}/{total_pages}):\n\n{genres_text}"

    # Кнопки навигации
    keyboard = []
    if page > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"show_genres_{page - 1}"))
    if page < total_pages - 1:
        keyboard.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"show_genres_{page + 1}"))
    reply_markup = InlineKeyboardMarkup([keyboard]) if keyboard else None
    
    # Отправка нового сообщения или редактирование существующего
    if update.callback_query:
        await update.callback_query.edit_message_text(message_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(message_text, reply_markup=reply_markup)

# Обработчик для кнопки «Показать все жанры»
async def handle_show_all_genres(update, context):
    await show_genres_page(update, context, page=0)

# Обработчик для навигации по страницам
async def handle_genre_navigation(update, context):
    query = update.callback_query
    page = int(query.data.split("_")[-1])
    await show_genres_page(update, context, page=page)