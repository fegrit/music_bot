import json
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from data.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Инициализация клиента Spotify
spotify = Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

# Функция для получения всех доступных жанров
def get_all_genres():
    genres = spotify.recommendation_genre_seeds()
    return genres['genres']

# Сохранение жанров в файл
def save_genres_to_file(filename="spotify_genres.json"):
    genres = get_all_genres()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(genres, f, ensure_ascii=False, indent=4)
    print(f"Жанры успешно сохранены в файл {filename}")

# Запуск функции сохранения
save_genres_to_file()