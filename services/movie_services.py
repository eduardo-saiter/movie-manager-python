from models.movie import Movie
from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
from models.media_search_result import MediaSearchResult
from mappers.omdb_mapper import (
    map_movie_from_omdb,
    map_search_results_from_omdb,
)
import requests
import sqlite3


class MovieServices:
    def __init__(self, api_client: MovieApiClient, repository: MovieRepository) -> None:
        self.api_client = api_client
        self.repository = repository

    def search_movie_by_title(self, user_search: str) -> Movie | None:

        if not user_search.strip():
            raise ValueError("O título não pode ser vazio.")

        return self.repository.search_data_movie(user_search)

    def search_movie_by_id(self, movie_id: int) -> Movie | None:

        return self.repository.search_movie_by_id(movie_id)

    def search_api_by_title(self, user_search: str) -> Movie:

        try:
            data = self.api_client.search_api(user_search.strip())

        except requests.Timeout as error:
            raise ConnectionError(
                "A API demorou demais para responder."
            ) from error

        except requests.ConnectionError as error:
            raise ConnectionError(
                "Não foi possível acessar a API, verifique sua internet."
            ) from error

        except requests.RequestException as error:
            raise ConnectionError(
                "Ocorreu um erro durante a comunicação com a API."
            ) from error

        return map_movie_from_omdb(data)

    def search_results(self, user_search: str,) -> list[MediaSearchResult]:

        search = user_search.strip()

        if not search:
            raise ValueError(
                "O título não pode ser vazio."
            )

        local_results = (
            self.repository.search_movie_results(search)
        )

        try:
            data = self.api_client.search_many(search)

        except requests.Timeout as error:
            raise ConnectionError(
                "A API demorou demais para responder."
            ) from error

        except requests.ConnectionError as error:
            raise ConnectionError(
                "Não foi possível acessar a API."
            ) from error

        except requests.RequestException as error:
            raise ConnectionError(
                "Erro durante a comunicação com a API."
            ) from error

        omdb_results = map_search_results_from_omdb(
            data
        )

        local_by_imdb_id = {
            result.imdb_id: result
            for result in local_results
            if result.imdb_id is not None
        }

        omdb_not_saved = [
            result
            for result in omdb_results
            if result.imdb_id not in local_by_imdb_id
        ]

        return [
            *local_results,
            *omdb_not_saved,
        ]

    def search_api_by_imdb_id(self, imdb_id: str,) -> Movie:

        if not imdb_id.strip():
            raise ValueError(
                "IMDb ID inválido."
            )

        try:
            data = self.api_client.search_by_imdb_id(
                imdb_id.strip()
            )

        except requests.Timeout as error:
            raise ConnectionError(
                "A API demorou demais para responder."
            ) from error

        except requests.ConnectionError as error:
            raise ConnectionError(
                "Não foi possível acessar a API."
            ) from error

        except requests.RequestException as error:
            raise ConnectionError(
                "Erro durante a comunicação com a API."
            ) from error

        return map_movie_from_omdb(data)

    def save_movie(self, movie: Movie) -> None:

        try:
            self.repository.save_movie(movie)

        except sqlite3.IntegrityError as error:
            raise ValueError(
                "Este filme já está salvo no catálogo."
            ) from error

    def list_saved_movies(self) -> list[Movie]:
        return self.repository.list_movies()

    def new_review_movie(self, movie_id: int, user_review: int | str,) -> None:

        try:
            review = int(user_review)

        except (TypeError, ValueError) as error:
            raise ValueError(
                "A avaliação deve ser um número inteiro."
            ) from error

        if not 0 <= review <= 5:
            raise ValueError(
                "A avaliação deve estar entre 0 e 5."
            )

        updated = self.repository.update_review(
            review,
            movie_id,
        )

        if not updated:
            raise ValueError(
                "O filme escolhido não foi encontrado."
            )

    def new_comment_movie(self, movie_id: int, user_comment: str,) -> None:

        comment = user_comment.strip()

        if not comment:
            raise ValueError(
                "O comentário não pode estar vazio."
            )

        if len(comment) > 500:
            raise ValueError(
                "O comentário deve ter no máximo 500 caracteres."
            )

        updated = self.repository.update_comment(
            comment,
            movie_id,
        )

        if not updated:
            raise ValueError(
                "O filme escolhido não foi encontrado."
            )

    def delete_saved_movie(self, movie_id: int,) -> None:

        deleted = self.repository.delete_movie(movie_id)

        if not deleted:
            raise ValueError(
                "O filme escolhido não foi encontrado."
            )
