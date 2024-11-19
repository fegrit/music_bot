from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CallbackContext
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from data.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from telegram import Update
from data import user_data
from handlers.menu import menu  # Импортируем для обновления меню

# Инициализация клиента Spotify
spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Проверка и загрузка жанров пользователя
def load_user_genres(user_id):
    user_data_dict = user_data.get_all_user_data()
    return user_data_dict.get(str(user_id), {}).get("genres", [])

# Функция для получения рекомендаций через Spotify API
def fetch_spotify_recommendations(user_genres, limit=10):
    recommendations = spotify.recommendations(seed_genres=user_genres, limit=limit)
    tracks = []
    for track in recommendations['tracks']:
        if track['preview_url']:
            tracks.append({
                "title": track['name'],
                "artist": track['artists'][0]['name'],
                "cover": track['album']['images'][0]['url'] if track['album']['images'] else None,
                "snippet": track['preview_url'],
                "spotify": track['external_urls']['spotify']
            })
    return tracks

# Отправка рекомендаций с проверкой жанров
async def get_recommendation(update: Update, context: CallbackContext, edit_message=False):
    if update.message:
        chat = update.message
    elif update.callback_query:
        chat = update.callback_query.message
    else:
        print("Не удалось определить источник сообщения")
        return

    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    user_data.set_state(user_id, "in_recommendations")  # Устанавливаем состояние рекомендаций
    user_genres = load_user_genres(user_id)

    if not user_genres:
        message = "У вас нет выбранных жанров. Пожалуйста, выберите жанры в настройках, чтобы получать рекомендации."
        await chat.reply_text(message)
        await menu(update, context)  # Возвращаем меню
        return

    tracks = fetch_spotify_recommendations(user_genres, limit=10)
    track = next((t for t in tracks if t["snippet"]), None)

    if not track:
        message = "К сожалению, для выбранных жанров отсутствуют треки с фрагментами для прослушивания."
        await chat.reply_text(message)
        await menu(update, context)  # Возвращаем меню
        return

    # Сохранение текущего трека
    context.user_data["current_track"] = track

    keyboard = [
        [InlineKeyboardButton("👍 Понравилось", callback_data="like"), InlineKeyboardButton("👎 Не понравилось", callback_data="dislike")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с обложкой и текстом
    if edit_message:
        media = InputMediaPhoto(media=track["cover"], caption=f"🎶 *{track['title']}* — *{track['artist']}*\nСлушайте фрагмент ниже.", parse_mode="Markdown")
        await chat.edit_media(media, reply_markup=reply_markup)
    else:
        sent_message = await chat.reply_photo(
            photo=track["cover"],
            caption=f"🎶 *{track['title']}* — *{track['artist']}*\nСлушайте фрагмент ниже.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        context.user_data.setdefault("session_messages", []).append(sent_message.message_id)

    # Удаляем предыдущее сообщение с аудиофайлом, если оно есть
    if "last_audio_message" in context.user_data:
        try:
            await context.user_data["last_audio_message"].delete()
        except Exception as e:
            print(f"Ошибка при удалении предыдущего аудиофайла: {e}")

    # Отправляем новый аудиофайл
    audio_title = f"(snippet) {track['title']} - {track['artist']}"
    audio_message = await chat.reply_audio(audio=track["snippet"], title=audio_title)
    context.user_data["last_audio_message"] = audio_message

# Обработка "Понравилось" и "Не понравилось"
async def handle_like_dislike(update: Update, context: CallbackContext):
    query = update.callback_query
    track = context.user_data.get("current_track")

    await query.answer()
    if query.data == "like":
        keyboard = [
            [InlineKeyboardButton("Spotify", callback_data="spotify")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(caption=f"Вы выбрали трек: *{track['title']}*\nВыберите платформу:", parse_mode="Markdown", reply_markup=reply_markup)
    elif query.data == "dislike":
        await get_recommendation(update, context, edit_message=True)

# Функция отправки ссылки на платформу
async def send_track_link(update: Update, context: CallbackContext):
    query = update.callback_query
    track = context.user_data.get("current_track")

    await query.answer()

    if query.data == "spotify":
        await delete_first_post(context)

        keyboard = [
            [InlineKeyboardButton("Продолжить", callback_data="continue")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(f"Слушайте трек на Spotify: {track['spotify']}", reply_markup=reply_markup)
    elif query.data == "continue":
        print("Кнопка 'Продолжить' нажата. Вызывается get_recommendation...")
        await clear_session_messages(context)
        await get_recommendation(update, context, edit_message=False)

# Удаление первого сообщения с обложкой и сниппетом
async def delete_first_post(context: CallbackContext):
    if "session_messages" in context.user_data and context.user_data["session_messages"]:
        message_id = context.user_data["session_messages"].pop(0)
        try:
            await context.bot.delete_message(chat_id=context.user_data["chat_id"], message_id=message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

# Очистка всех сообщений текущей сессии
async def clear_session_messages(context: CallbackContext):
    if "session_messages" in context.user_data:
        for message_id in context.user_data["session_messages"]:
            try:
                await context.bot.delete_message(chat_id=context.user_data["chat_id"], message_id=message_id)
            except Exception as e:
                print(f"Ошибка при удалении сообщения: {e}")
        context.user_data["session_messages"] = []