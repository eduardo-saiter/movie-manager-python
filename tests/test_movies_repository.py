from collections.abc import Callable
import sqlite3

import pytest

from models.movie import Movie
from repositories.movies_repository import MovieRepository


def test_save_movie_inserts_data_and_assigns_id(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()

    result = movie_repository.save_movie(movie)

    assert result is movie
    assert movie.id == 1

    saved = movie_repository.search_data_movie_id(1)
    assert saved is not None
    assert saved.title == movie.title
    assert saved.year == 2014
    assert saved.poster == movie.poster


def test_search_movie_is_case_insensitive_and_ignores_spaces(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory(title="Interstellar"))

    result = movie_repository.search_data_movie("  INTERSTELLAR  ")

    assert result is not None
    assert result.title == "Interstellar"


def test_search_movie_returns_none_when_missing(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.search_data_movie("Missing") is None


def test_search_movie_by_id_returns_none_when_missing(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.search_data_movie_id(999) is None


def test_list_movies_returns_all_saved_movies(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    first = movie_factory(title="Interstellar")
    second = movie_factory(title="Arrival", year="2016")
    movie_repository.save_movie(first)
    movie_repository.save_movie(second)

    result = movie_repository.list_movies()

    assert [movie.title for movie in result] == ["Interstellar", "Arrival"]
    assert [movie.id for movie in result] == [1, 2]


def test_list_movies_returns_empty_list(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.list_movies() == []


def test_update_review(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_repository.save_movie(movie_factory())

    movie_repository.update_review(5, movie.id)  # type: ignore[arg-type]

    updated = movie_repository.search_data_movie_id(movie.id)  # type: ignore[arg-type]
    assert updated is not None
    assert updated.avaliation == 5


def test_update_comment(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_repository.save_movie(movie_factory())

    movie_repository.update_comment("Excelente", movie.id)  # type: ignore[arg-type]

    updated = movie_repository.search_data_movie_id(movie.id)  # type: ignore[arg-type]
    assert updated is not None
    assert updated.comment == "Excelente"


def test_delete_movie(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_repository.save_movie(movie_factory())

    movie_repository.delete_movie(movie.id)  # type: ignore[arg-type]

    assert movie_repository.search_data_movie_id(movie.id) is None  # type: ignore[arg-type]


def test_duplicate_title_raises_integrity_error(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory(title="Interstellar"))

    with pytest.raises(sqlite3.IntegrityError):
        movie_repository.save_movie(movie_factory(title="INTERSTELLAR"))
