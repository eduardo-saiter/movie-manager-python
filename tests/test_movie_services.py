from collections.abc import Callable
import sqlite3
from unittest.mock import Mock

import pytest
import requests

from models.movie import Movie
from services.movie_services import MovieServices


def api_movie_data(**overrides: str) -> dict[str, str]:
    data = {
        "Response": "True",
        "Title": "Interstellar",
        "Year": "2014",
        "Genre": "Adventure, Drama, Sci-Fi",
        "Director": "Christopher Nolan",
        "Plot": "Exploradores atravessam um buraco de minhoca.",
        "Poster": "https://example.com/interstellar.jpg",
    }
    data.update(overrides)
    return data


def test_search_movie_rejects_blank_title(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    with pytest.raises(ValueError, match="título não pode ser vazio"):
        movie_service.search_movie_by_title("   ")

    repository_mock.search_data_movie.assert_not_called()


def test_search_movie_returns_repository_result(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=1)
    repository_mock.search_data_movie.return_value = movie

    result = movie_service.search_movie_by_title("Interstellar")

    assert result == movie
    repository_mock.search_data_movie.assert_called_once_with("Interstellar")


def test_search_movie_by_id_returns_repository_result(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=1)
    repository_mock.search_data_movie_id.return_value = movie

    assert movie_service.search_movie_by_id(1) == movie
    repository_mock.search_data_movie_id.assert_called_once_with(1)


def test_search_api_builds_movie(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_api.return_value = api_movie_data()

    result = movie_service.search_api_by_title("  Interstellar  ")

    assert result == Movie(
        title="Interstellar",
        year="2014",
        genre="Adventure, Drama, Sci-Fi",
        director="Christopher Nolan",
        plot="Exploradores atravessam um buraco de minhoca.",
        poster="https://example.com/interstellar.jpg",
    )
    api_client_mock.search_api.assert_called_once_with("Interstellar")


def test_search_api_converts_na_poster_to_none(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_api.return_value = api_movie_data(Poster="N/A")

    result = movie_service.search_api_by_title("Interstellar")

    assert result.poster is None


def test_search_api_raises_when_movie_is_not_found(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_api.return_value = {
        "Response": "False",
        "Error": "Movie not found!",
    }

    with pytest.raises(ValueError, match="Filme não encontrado"):
        movie_service.search_api_by_title("Missing")


@pytest.mark.parametrize(
    ("api_error", "message"),
    [
        (requests.Timeout(), "demorou demais"),
        (requests.ConnectionError(), "verifique sua internet"),
        (requests.RequestException(), "erro durante a comunicação"),
    ],
)
def test_search_api_converts_request_errors_to_connection_error(
    movie_service: MovieServices,
    api_client_mock: Mock,
    api_error: requests.RequestException,
    message: str,
) -> None:
    api_client_mock.search_api.side_effect = api_error

    with pytest.raises(ConnectionError, match=message):
        movie_service.search_api_by_title("Interstellar")


def test_save_movie_calls_repository(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()

    movie_service.save_movie(movie)

    repository_mock.save_movie.assert_called_once_with(movie)


def test_save_movie_converts_duplicate_error_to_value_error(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.save_movie.side_effect = sqlite3.IntegrityError()

    with pytest.raises(ValueError, match="já está salvo"):
        movie_service.save_movie(movie_factory())


def test_list_saved_movies_returns_repository_list(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movies = [movie_factory(id=1)]
    repository_mock.list_movies.return_value = movies

    assert movie_service.list_saved_movies() == movies


def test_new_review_rejects_missing_movie(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.search_data_movie_id.return_value = None

    with pytest.raises(ValueError, match="não foi encontrado"):
        movie_service.new_review_movie(999, 5)


def test_new_review_rejects_blank_string(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    with pytest.raises(ValueError, match="não pode estar vazia"):
        movie_service.new_review_movie(1, "   ")


def test_new_review_rejects_non_numeric_value(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    with pytest.raises(ValueError, match="número válido"):
        movie_service.new_review_movie(1, "cinco")


@pytest.mark.parametrize("review", [-1, 6, "-1", "6"])
def test_new_review_rejects_values_outside_range(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
    review: int | str,
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    with pytest.raises(ValueError, match="entre 0 e 5"):
        movie_service.new_review_movie(1, review)


@pytest.mark.parametrize(("review", "expected"), [(0, 0), ("5", 5)])
def test_new_review_accepts_web_and_console_values(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
    review: int | str,
    expected: int,
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    movie_service.new_review_movie(1, review)

    repository_mock.update_review.assert_called_once_with(expected, 1)


def test_new_comment_rejects_missing_movie(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.search_data_movie_id.return_value = None

    with pytest.raises(ValueError, match="não foi encontrado"):
        movie_service.new_comment_movie(999, "Ótimo")


@pytest.mark.parametrize("comment", ["", "   "])
def test_new_comment_rejects_blank_comment(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
    comment: str,
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    with pytest.raises(ValueError, match="não pode ser vazio"):
        movie_service.new_comment_movie(1, comment)


def test_new_comment_rejects_more_than_500_characters(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    with pytest.raises(ValueError, match="500 caracteres"):
        movie_service.new_comment_movie(1, "a" * 501)


def test_new_comment_strips_spaces_before_update(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    movie_service.new_comment_movie(1, "   Filme excelente!   ")

    repository_mock.update_comment.assert_called_once_with(
        "Filme excelente!", 1)


def test_delete_saved_movie_calls_repository(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.search_data_movie_id.return_value = movie_factory(id=1)

    movie_service.delete_saved_movie(1)

    repository_mock.delete_movie.assert_called_once_with(1)


def test_delete_saved_movie_rejects_missing_movie(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.search_data_movie_id.return_value = None

    with pytest.raises(ValueError, match="não foi encontrado"):
        movie_service.delete_saved_movie(999)
