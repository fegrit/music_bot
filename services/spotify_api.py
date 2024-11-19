import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from data.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Настройка авторизации
auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
spotify = spotipy.Spotify(auth_manager=auth_manager)

# Получение списка доступных жанров
def get_genres():
    response = spotify.recommendation_genre_seeds()
    genres = response.get("genres", [])
    return genres

# Получение популярных исполнителей по выбранному жанру
def get_artists_by_genre(genre, limit=5):
    results = spotify.search(q=f"genre:{genre}", type="artist", limit=limit)
    artists = results["artists"]["items"]
    return [{"name": artist["name"], "id": artist["id"]} for artist in artists]