from collections.abc import Callable
import sqlite3
from unittest.mock import Mock

import pytest
import requests

from errors import (
    MovieAlreadySavedError,
    MovieApiConfigurationError,
    MovieNotFoundError,
)
from models.media_search_result import MediaSearchResult
from models.movie import Movie
from services.movie_services import MovieServices


def api_movie_data(**overrides: object) -> dict:
    data: dict[str, object] = {
        "Response": "True",
        "Title": "Interstellar",
        "Year": "2014",
        "Genre": "Adventure, Drama, Sci-Fi",
        "Director": "Christopher Nolan",
        "Plot": "Exploradores atravessam um buraco de minhoca.",
        "Poster": "https://example.com/interstellar.jpg",
        "Type": "movie",
        "imdbID": "tt0816692",
        "Runtime": "169 min",
        "Released": "07 Nov 2014",
        "imdbRating": "8.7",
        "imdbVotes": "2,400,000",
        "Metascore": "74",
        "BoxOffice": "$188,020,017",
        "Ratings": [],
    }
    data.update(overrides)
    return data


def api_search_data(*items: dict) -> dict:
    return {
        "Response": "True",
        "Search": list(items),
        "totalResults": str(len(items)),
    }


def search_item(
    title: str = "Interstellar",
    imdb_id: str = "tt0816692",
) -> dict:
    return {
        "Title": title,
        "Year": "2014",
        "imdbID": imdb_id,
        "Type": "movie",
        "Poster": "https://example.com/poster.jpg",
    }


def test_search_movie_rejects_blank_title(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    with pytest.raises(ValueError, match="título não pode ser vazio"):
        movie_service.search_movie_by_title("   ")

    repository_mock.search_data_movie.assert_not_called()


def test_search_movie_normalizes_and_returns_repository_result(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=1)
    repository_mock.search_data_movie.return_value = movie

    result = movie_service.search_movie_by_title("  Interstellar  ")

    assert result == movie
    repository_mock.search_data_movie.assert_called_once_with("Interstellar")


def test_search_movie_by_id_returns_repository_result(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(id=1)
    repository_mock.search_movie_by_id.return_value = movie

    assert movie_service.search_movie_by_id(1) == movie
    repository_mock.search_movie_by_id.assert_called_once_with(1)


def test_search_api_by_title_rejects_blank_title(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    with pytest.raises(ValueError, match="título não pode ser vazio"):
        movie_service.search_api_by_title("   ")

    api_client_mock.search_api.assert_not_called()


def test_search_api_by_title_builds_movie(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_api.return_value = api_movie_data()

    result = movie_service.search_api_by_title("  Interstellar  ")

    assert result.title == "Interstellar"
    assert result.year == 2014
    assert result.media_type == "movie"
    assert result.imdb_id == "tt0816692"
    api_client_mock.search_api.assert_called_once_with("Interstellar")


def test_search_api_by_title_translates_not_found(
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
def test_search_api_by_title_converts_request_errors(
    movie_service: MovieServices,
    api_client_mock: Mock,
    api_error: requests.RequestException,
    message: str,
) -> None:
    api_client_mock.search_api.side_effect = api_error

    with pytest.raises(ConnectionError, match=message):
        movie_service.search_api_by_title("Interstellar")


def test_search_api_by_title_converts_missing_api_key(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_api.side_effect = MovieApiConfigurationError(
        "OMDB_API_KEY não encontrada."
    )

    with pytest.raises(ConnectionError, match="não foi configurada"):
        movie_service.search_api_by_title("Interstellar")


def test_search_results_rejects_blank_title(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    with pytest.raises(ValueError, match="título não pode ser vazio"):
        movie_service.search_results("   ")

    repository_mock.search_movie_results.assert_not_called()


def test_search_results_combines_local_and_omdb_results(
    movie_service: MovieServices,
    repository_mock: Mock,
    api_client_mock: Mock,
    search_result_factory: Callable[..., MediaSearchResult],
) -> None:
    local = search_result_factory(local_id=1)
    repository_mock.search_movie_results.return_value = [local]
    repository_mock.find_local_ids_by_imdb_ids.return_value = {
        "tt0816692": 1
    }
    api_client_mock.search_many.return_value = api_search_data(
        search_item(),
        search_item("Interstate 60", "tt0165832"),
    )

    results = movie_service.search_results(" inter ")

    assert [result.title for result in results] == [
        "Interstellar",
        "Interstate 60",
    ]
    assert results[0].local_id == 1
    assert results[1].local_id is None
    api_client_mock.search_many.assert_called_once_with("inter")


def test_search_results_marks_omdb_item_as_local_even_when_local_search_misses(
    movie_service: MovieServices,
    repository_mock: Mock,
    api_client_mock: Mock,
) -> None:
    repository_mock.search_movie_results.return_value = []
    repository_mock.find_local_ids_by_imdb_ids.return_value = {
        "tt0816692": 7
    }
    api_client_mock.search_many.return_value = api_search_data(search_item())

    results = movie_service.search_results("inter")

    assert len(results) == 1
    assert results[0].local_id == 7


def test_search_results_matches_legacy_local_movie_without_imdb_id(
    movie_service: MovieServices,
    repository_mock: Mock,
    api_client_mock: Mock,
    search_result_factory: Callable[..., MediaSearchResult],
) -> None:
    local = search_result_factory(
        local_id=4,
        imdb_id=None,
        title="Interstellar",
        year="2014",
    )
    repository_mock.search_movie_results.return_value = [local]
    repository_mock.find_local_ids_by_imdb_ids.return_value = {}
    api_client_mock.search_many.return_value = api_search_data(search_item())

    results = movie_service.search_results("inter")

    assert results == [local]
    assert results[0].local_id == 4


def test_search_results_removes_duplicate_omdb_ids(
    movie_service: MovieServices,
    repository_mock: Mock,
    api_client_mock: Mock,
) -> None:
    repository_mock.search_movie_results.return_value = []
    repository_mock.find_local_ids_by_imdb_ids.return_value = {}
    api_client_mock.search_many.return_value = api_search_data(
        search_item(),
        search_item(),
    )

    results = movie_service.search_results("inter")

    assert len(results) == 1


def test_search_results_returns_local_results_when_omdb_has_no_matches(
    movie_service: MovieServices,
    repository_mock: Mock,
    api_client_mock: Mock,
    search_result_factory: Callable[..., MediaSearchResult],
) -> None:
    local = search_result_factory(local_id=1)
    repository_mock.search_movie_results.return_value = [local]
    repository_mock.find_local_ids_by_imdb_ids.return_value = {}
    api_client_mock.search_many.return_value = {
        "Response": "False",
        "Error": "Movie not found!",
    }

    assert movie_service.search_results("inter") == [local]


@pytest.mark.parametrize(
    ("api_error", "message"),
    [
        (requests.Timeout(), "demorou demais"),
        (requests.ConnectionError(), "Não foi possível acessar"),
        (requests.RequestException(), "Erro durante"),
    ],
)
def test_search_results_converts_request_errors(
    movie_service: MovieServices,
    repository_mock: Mock,
    api_client_mock: Mock,
    api_error: requests.RequestException,
    message: str,
) -> None:
    repository_mock.search_movie_results.return_value = []
    api_client_mock.search_many.side_effect = api_error

    with pytest.raises(ConnectionError, match=message):
        movie_service.search_results("inter")


def test_search_api_by_imdb_id_rejects_blank_id(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    with pytest.raises(ValueError, match="IMDb ID inválido"):
        movie_service.search_api_by_imdb_id("   ")

    api_client_mock.search_by_imdb_id.assert_not_called()


def test_search_api_by_imdb_id_builds_movie(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_by_imdb_id.return_value = api_movie_data()

    result = movie_service.search_api_by_imdb_id(" tt0816692 ")

    assert result.imdb_id == "tt0816692"
    api_client_mock.search_by_imdb_id.assert_called_once_with("tt0816692")


def test_search_api_by_imdb_id_converts_request_error(
    movie_service: MovieServices,
    api_client_mock: Mock,
) -> None:
    api_client_mock.search_by_imdb_id.side_effect = requests.Timeout()

    with pytest.raises(ConnectionError, match="demorou demais"):
        movie_service.search_api_by_imdb_id("tt0816692")


def test_save_movie_calls_repository(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()

    movie_service.save_movie(movie)

    repository_mock.save_movie.assert_called_once_with(movie)


def test_save_movie_rejects_missing_imdb_id(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    with pytest.raises(ValueError, match="sem IMDb ID"):
        movie_service.save_movie(movie_factory(imdb_id=None))

    repository_mock.save_movie.assert_not_called()


def test_save_movie_rejects_invalid_review(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    with pytest.raises(ValueError, match="entre 0 e 5"):
        movie_service.save_movie(movie_factory(avaliation=6))

    repository_mock.save_movie.assert_not_called()


def test_save_movie_normalizes_text_fields(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory(
        title="  Interstellar  ",
        imdb_id="  tt0816692  ",
        comment="  Excelente  ",
    )

    movie_service.save_movie(movie)

    assert movie.title == "Interstellar"
    assert movie.imdb_id == "tt0816692"
    assert movie.comment == "Excelente"
    repository_mock.save_movie.assert_called_once_with(movie)


def test_save_movie_rejects_blank_title(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    with pytest.raises(ValueError, match="título não pode ser vazio"):
        movie_service.save_movie(movie_factory(title="   "))

    repository_mock.save_movie.assert_not_called()


def test_save_movie_rejects_long_initial_comment(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    with pytest.raises(ValueError, match="no máximo 500"):
        movie_service.save_movie(movie_factory(comment="a" * 501))

    repository_mock.save_movie.assert_not_called()


def test_save_movie_converts_duplicate_error_to_value_error(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.save_movie.side_effect = sqlite3.IntegrityError(
        "UNIQUE constraint failed: media.imdb_id"
    )

    with pytest.raises(MovieAlreadySavedError, match="já está salvo"):
        movie_service.save_movie(movie_factory())


def test_save_movie_does_not_hide_other_integrity_errors(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    repository_mock.save_movie.side_effect = sqlite3.IntegrityError(
        "UNIQUE constraint failed: external_ratings.media_id, "
        "external_ratings.source"
    )

    with pytest.raises(sqlite3.IntegrityError, match="external_ratings"):
        movie_service.save_movie(movie_factory())


def test_list_saved_movies_returns_repository_list(
    movie_service: MovieServices,
    repository_mock: Mock,
    movie_factory: Callable[..., Movie],
) -> None:
    movies = [movie_factory(id=1)]
    repository_mock.list_movies.return_value = movies

    assert movie_service.list_saved_movies() == movies


@pytest.mark.parametrize("review", [0, "5"])
def test_new_review_accepts_web_and_console_values(
    movie_service: MovieServices,
    repository_mock: Mock,
    review: int | str,
) -> None:
    repository_mock.update_review.return_value = True

    movie_service.new_review_movie(1, review)

    repository_mock.update_review.assert_called_once_with(int(review), 1)


def test_new_review_rejects_blank_value(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    with pytest.raises(ValueError, match="não pode estar vazia"):
        movie_service.new_review_movie(1, "   ")

    repository_mock.update_review.assert_not_called()


def test_new_review_rejects_non_numeric_value(
    movie_service: MovieServices,
) -> None:
    with pytest.raises(ValueError, match="número inteiro"):
        movie_service.new_review_movie(1, "cinco")


@pytest.mark.parametrize("review", [-1, 6, "-1", "6"])
def test_new_review_rejects_values_outside_range(
    movie_service: MovieServices,
    review: int | str,
) -> None:
    with pytest.raises(ValueError, match="entre 0 e 5"):
        movie_service.new_review_movie(1, review)


def test_new_review_rejects_missing_movie(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.update_review.return_value = False

    with pytest.raises(MovieNotFoundError, match="não foi encontrado"):
        movie_service.new_review_movie(999, 5)


def test_new_comment_strips_spaces_before_update(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.update_comment.return_value = True

    movie_service.new_comment_movie(1, "   Filme excelente!   ")

    repository_mock.update_comment.assert_called_once_with(
        "Filme excelente!",
        1,
    )


@pytest.mark.parametrize("comment", ["", "   "])
def test_new_comment_rejects_blank_comment(
    movie_service: MovieServices,
    comment: str,
) -> None:
    with pytest.raises(ValueError, match="não pode estar vazio"):
        movie_service.new_comment_movie(1, comment)


def test_new_comment_rejects_more_than_500_characters(
    movie_service: MovieServices,
) -> None:
    with pytest.raises(ValueError, match="500 caracteres"):
        movie_service.new_comment_movie(1, "a" * 501)


def test_new_comment_rejects_missing_movie(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.update_comment.return_value = False

    with pytest.raises(MovieNotFoundError, match="não foi encontrado"):
        movie_service.new_comment_movie(999, "Ótimo")


def test_delete_saved_movie_calls_repository(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.delete_movie.return_value = True

    movie_service.delete_saved_movie(1)

    repository_mock.delete_movie.assert_called_once_with(1)


def test_delete_saved_movie_rejects_missing_movie(
    movie_service: MovieServices,
    repository_mock: Mock,
) -> None:
    repository_mock.delete_movie.return_value = False

    with pytest.raises(MovieNotFoundError, match="não foi encontrado"):
        movie_service.delete_saved_movie(999)
