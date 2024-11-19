import json
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from data import user_data
from data.config import welcome_images
from handlers.menu import menu  # Импортируем главное меню
from genre_pagination import handle_show_all_genres, handle_genre_navigation  # Импортируем обработчики для показа всех жанров

# Загрузка переводов жанров
try:
    with open("data/genre_translations.json", "r", encoding="utf-8") as f:
        GENRE_TRANSLATION = json.load(f)
except Exception as e:
    print("Ошибка при загрузке GENRE_TRANSLATION:", e)

# Основные жанры на русском
MAIN_GENRES = ["поп", "рок", "джаз", "классическая", "электронная", "хип-хоп", "блюз", "регги", "кантри", "r&b"]

# Приветственное сообщение и выбор жанров
async def start(update, context):
    user_id = update.message.from_user.id
    user_data.init_user(user_id)

    # Проверяем, есть ли у пользователя данные
    if user_data.user_exists(user_id) and user_data.get_user_genres(user_id):
        user_data.set_state(user_id, "menu")  # Устанавливаем состояние "menu"
        print(f"Переход в меню для пользователя {user_id} с уже выбранными жанрами.")  # Отладочный вывод
        await menu(update, context)  # Сразу переходим в меню, если данные уже есть
        return

    # Если данных нет, устанавливаем состояние "awaiting_genres"
    user_data.set_state(user_id, "awaiting_genres")
    print(f"Установлено состояние 'awaiting_genres' для пользователя {user_id}")  # Отладочный вывод

    # Приветственное сообщение
    welcome_image = random.choice(welcome_images)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(welcome_image, 'rb'),
        caption="Добро пожаловать! Я - твои новые рекомендации в музыке 💚"
    )

    # Формируем список основных жанров на русском
    main_genres_list = ", ".join(MAIN_GENRES)
    keyboard = [[InlineKeyboardButton("Показать все жанры", callback_data="show_all_genres")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    instruction_text = (
        "Пожалуйста, введите Ваши любимые музыкальные жанры через запятую (от 1-го до 4-х).\n\n"
        "Вот список основных жанров:\n\n"
        f"{main_genres_list}\n\n"
        "Или нажмите 'Показать все жанры', чтобы увидеть полный список."
    )

    await update.message.reply_text(instruction_text, reply_markup=reply_markup)