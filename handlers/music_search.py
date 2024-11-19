from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Update
from spotipy import Spotify
from data import user_data
from handlers.menu import menu  # Импортируем функцию menu, а не модуль
from spotipy.oauth2 import SpotifyClientCredentials
from data.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Обработка поиска музыки
async def handle_music_search(update: Update, context: CallbackContext):
    if update.message is None:  # Проверяем, что это текстовое сообщение
        return

    print(f"handle_music_search вызван. Сообщение пользователя: {update.message.text}")
    user_id = update.message.from_user.id
    query = update.message.text.strip()

    if not query:
        await update.message.reply_text("Введите поисковый запрос для поиска музыки.")
        return

    try:
        print(f"Поиск в Spotify для запроса: {query}")
        search_result = spotify.search(q=query, type="track", limit=1)
        print(f"Результаты поиска: {search_result}")

        if not search_result['tracks']['items']:
            await update.message.reply_text("К сожалению, ничего не найдено. Попробуйте другой запрос.")
            return

        track = search_result['tracks']['items'][0]
        track_info = {
            "title": track['name'],
            "artist": track['artists'][0]['name'],
            "cover": track['album']['images'][0]['url'] if track['album']['images'] else None,
            "snippet": track['preview_url'],
            "spotify": track['external_urls']['spotify']
        }

        context.user_data["current_track"] = track_info

        caption = (
            f"🎶 *{track_info['title']}* — *{track_info['artist']}*\n\n"
            f"[Слушать на Spotify]({track_info['spotify']})\n"
        )

        if track_info['cover']:
            print("Отправка обложки трека")
            await update.message.reply_photo(
                photo=track_info['cover'],
                caption=caption,
                parse_mode="Markdown"
            )

        if track_info['snippet']:
            print("Отправка сниппета трека")
            await update.message.reply_audio(
                audio=track_info['snippet'],
                title=f"{track_info['title']} - {track_info['artist']}"
            )
        else:
            print("Сниппет отсутствует")
            await update.message.reply_text("К сожалению, для этого трека нет доступного сниппета.")

    except Exception as e:
        print(f"Ошибка в handle_music_search: {e}")
        await update.message.reply_text("Ошибка при выполнении поиска. Попробуйте снова.")

# Обработка выхода из поиска
async def handle_exit(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    print(f"Пользователь {user_id} вышел из поиска.")
    await update.callback_query.answer()  # Подтверждаем нажатие кнопки

    # Сбрасываем состояние пользователя
    user_data.set_state(user_id, None)

    # Отправляем сообщение о возвращении в главное меню
    await update.callback_query.message.reply_text(
        "Вы вернулись в главное меню. Чем могу помочь?"
    )

    # Вызываем главное меню
    await menu(update, context)

# Функция для инициации поиска
async def find_music(update, context):
    user_id = update.message.from_user.id
    user_data.set_state(user_id, "awaiting_music_query")
    print(f"find_music вызван. Состояние пользователя: awaiting_music_query")

    await update.message.reply_text(
        "Введите название трека, имя артиста или и то, и другое, чтобы найти музыку.",
    )

    # Обновляем меню
    await menu(update, context)