import json
import os

# Файлы данных
USER_DATA_FILE = "user_data.json"
TRANSLATION_FILE = "genre_translations.json"

# Глобальные переменные
user_states = {}

# Загрузка переводов жанров из файла
def load_genre_translations():
    if os.path.exists(TRANSLATION_FILE):
        try:
            with open(TRANSLATION_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке переводов жанров: {e}")
            return {}
    else:
        print(f"Файл переводов жанров '{TRANSLATION_FILE}' не найден.")
        return {}

# Загружаем переводы жанров в словарь
GENRE_TRANSLATION = load_genre_translations()

# Загрузка всех данных пользователей
def load_user_data():
    global user_states
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
                user_states = json.load(file)
        except Exception as e:
            print(f"Ошибка при загрузке данных пользователей: {e}")
            user_states = {}
    else:
        print(f"Файл данных пользователей '{USER_DATA_FILE}' не найден. Инициализация пустых данных.")
        user_states = {}

# Сохранение всех данных пользователей, перезаписывая файл
def save_user_data():
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(user_states, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных пользователей: {e}")

# Проверка, существует ли пользователь
def user_exists(user_id):
    return str(user_id) in user_states

# Инициализация пользователя, если его нет
def init_user(user_id):
    user_states.setdefault(str(user_id), {
        "genres": [],
        "state": "awaiting_start"
    })
    save_user_data()

# Установка состояния пользователя
def set_state(user_id, state):
    user_id = str(user_id)
    if user_id not in user_states:
        init_user(user_id)
    user_states[user_id]["state"] = state
    save_user_data()

# Получение состояния пользователя
def get_state(user_id):
    return user_states.get(str(user_id), {}).get("state", "awaiting_start")

# Добавление жанра пользователю с переводом
def add_genre(user_id, genre):
    user_id = str(user_id)
    # Проверка, существует ли перевод для жанра
    english_genre = next((k for k, v in GENRE_TRANSLATION.items() if v == genre), genre)

    if english_genre == genre:
        print(f"Предупреждение: перевод для жанра '{genre}' отсутствует.")

    if "genres" not in user_states[user_id]:
        user_states[user_id]["genres"] = []

    # Проверка на дублирование
    if english_genre not in user_states[user_id]["genres"]:
        user_states[user_id]["genres"].append(english_genre)
        save_user_data()
    else:
        print(f"Жанр '{english_genre}' уже добавлен пользователю {user_id}.")

# Получение жанров пользователя (переведенные на русский)
def get_user_genres(user_id):
    genres = user_states.get(str(user_id), {}).get("genres", [])
    return [GENRE_TRANSLATION.get(genre, genre) for genre in genres]

# Функция для получения всех данных пользователей
def get_all_user_data():
    return user_states

# Загрузка данных при запуске
load_user_data()