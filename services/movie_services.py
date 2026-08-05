import sqlite3

import requests

from clients.movie_api_client import MovieApiClient
from errors import (
    MovieAlreadySavedError,
    MovieApiConfigurationError,
    MovieNotFoundError,
)
from mappers.omdb_mapper import (
    map_movie_from_omdb,
    map_search_results_from_omdb,
)
from models.media_search_result import MediaSearchResult
from models.movie import Movie
from repositories.movies_repository import MovieRepository


class MovieServices:
    def __init__(
        self,
        api_client: MovieApiClient,
        repository: MovieRepository,
    ) -> None:
        self.api_client = api_client
        self.repository = repository

    def search_movie_by_title(self, user_search: str) -> Movie | None:
        search = user_search.strip()
        if not search:
            raise ValueError("O título não pode ser vazio.")

        return self.repository.search_data_movie(search)

    def search_movie_by_id(self, movie_id: int) -> Movie | None:
        return self.repository.search_movie_by_id(movie_id)

    def search_api_by_title(self, user_search: str) -> Movie:
        search = user_search.strip()
        if not search:
            raise ValueError("O título não pode ser vazio.")

        try:
            data = self.api_client.search_api(search)
        except MovieApiConfigurationError as error:
            raise ConnectionError(
                "A chave da OMDb não foi configurada."
            ) from error
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

    def search_results(
        self,
        user_search: str,
    ) -> list[MediaSearchResult]:
        search = user_search.strip()
        if not search:
            raise ValueError("O título não pode ser vazio.")

        local_results = self.repository.search_movie_results(search)

        try:
            data = self.api_client.search_many(search)
        except MovieApiConfigurationError as error:
            raise ConnectionError(
                "A chave da OMDb não foi configurada."
            ) from error
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

        omdb_results = map_search_results_from_omdb(data)
        omdb_ids = [
            result.imdb_id
            for result in omdb_results
            if result.imdb_id is not None
        ]
        saved_ids = self.repository.find_local_ids_by_imdb_ids(omdb_ids)

        local_by_title_year = {
            (
                result.title.strip().casefold(),
                result.year[:4] if result.year else None,
            ): result.local_id
            for result in local_results
            if result.local_id is not None
        }

        for result in omdb_results:
            if result.imdb_id is not None:
                result.local_id = saved_ids.get(result.imdb_id.casefold())

            if result.local_id is None:
                result.local_id = local_by_title_year.get(
                    (
                        result.title.strip().casefold(),
                        result.year[:4] if result.year else None,
                    )
                )

        combined_results = [*local_results, *omdb_results]
        unique_results: list[MediaSearchResult] = []
        seen: set[tuple[object, ...]] = set()

        for result in combined_results:
            if result.local_id is not None:
                key: tuple[object, ...] = ("local", result.local_id)
            elif result.imdb_id is not None:
                key = (
                    "imdb",
                    result.imdb_id.casefold(),
                )
            else:
                key = (
                    "title",
                    result.title.casefold(),
                    result.year,
                    result.media_type,
                )

            if key in seen:
                continue

            seen.add(key)
            unique_results.append(result)

        return unique_results

    def search_api_by_imdb_id(self, imdb_id: str) -> Movie:
        normalized_id = imdb_id.strip()
        if not normalized_id:
            raise ValueError("IMDb ID inválido.")

        try:
            data = self.api_client.search_by_imdb_id(normalized_id)
        except MovieApiConfigurationError as error:
            raise ConnectionError(
                "A chave da OMDb não foi configurada."
            ) from error
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
        movie.title = movie.title.strip()
        if not movie.title:
            raise ValueError("O título não pode ser vazio.")

        if movie.imdb_id is None or not movie.imdb_id.strip():
            raise ValueError(
                "Não é possível salvar um filme sem IMDb ID."
            )
        movie.imdb_id = movie.imdb_id.strip()

        if not 0 <= movie.avaliation <= 5:
            raise ValueError(
                "A avaliação deve estar entre 0 e 5."
            )

        if movie.comment is not None:
            comment = movie.comment.strip()
            if len(comment) > 500:
                raise ValueError(
                    "O comentário deve ter no máximo 500 caracteres."
                )
            movie.comment = comment or None

        try:
            self.repository.save_movie(movie)
        except sqlite3.IntegrityError as error:
            error_message = str(error).casefold()

            duplicate_imdb_id = (
                "media.imdb_id" in error_message
                or "ux_media_imdb_id_nocase" in error_message
            )

            if duplicate_imdb_id:
                raise MovieAlreadySavedError(
                    "Este filme já está salvo no catálogo."
                ) from error

            raise

    def list_saved_movies(self) -> list[Movie]:
        return self.repository.list_movies()

    def new_review_movie(
        self,
        movie_id: int,
        user_review: int | str,
    ) -> None:
        if isinstance(user_review, str) and not user_review.strip():
            raise ValueError("A avaliação não pode estar vazia.")

        try:
            review = int(user_review)
        except (TypeError, ValueError) as error:
            raise ValueError(
                "A avaliação deve ser um número inteiro."
            ) from error

        if not 0 <= review <= 5:
            raise ValueError("A avaliação deve estar entre 0 e 5.")

        updated = self.repository.update_review(review, movie_id)
        if not updated:
            raise MovieNotFoundError(
                "O filme escolhido não foi encontrado."
            )

    def new_comment_movie(
        self,
        movie_id: int,
        user_comment: str,
    ) -> None:
        comment = user_comment.strip()

        if not comment:
            raise ValueError("O comentário não pode estar vazio.")
        if len(comment) > 500:
            raise ValueError(
                "O comentário deve ter no máximo 500 caracteres."
            )

        updated = self.repository.update_comment(comment, movie_id)
        if not updated:
            raise MovieNotFoundError(
                "O filme escolhido não foi encontrado."
            )

    def delete_saved_movie(self, movie_id: int) -> None:
        deleted = self.repository.delete_movie(movie_id)
        if not deleted:
            raise MovieNotFoundError(
                "O filme escolhido não foi encontrado."
            )
