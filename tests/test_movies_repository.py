from collections.abc import Callable
from datetime import datetime
import sqlite3

import pytest

from models.external_rating import ExternalRating
from models.movie import Movie
from repositories.movies_repository import MovieRepository


def test_save_movie_inserts_complete_data_and_assigns_ids(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()

    result = movie_repository.save_movie(movie)

    assert result is None
    assert movie.id == 1
    assert all(rating.id is not None for rating in movie.external_ratings)
    assert all(rating.media_id == 1 for rating in movie.external_ratings)

    saved = movie_repository.search_movie_by_id(1)
    assert saved is not None
    assert saved.title == movie.title
    assert saved.year == 2014
    assert saved.director == movie.director
    assert saved.poster == movie.poster
    assert saved.released_at == movie.released_at
    assert saved.imdb_votes == movie.imdb_votes
    assert saved.created_at is not None
    assert saved.updated_at is not None


def test_save_movie_persists_external_ratings(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()
    movie_repository.save_movie(movie)

    saved = movie_repository.search_movie_by_id(movie.id)  # type: ignore[arg-type]

    assert saved is not None
    assert [rating.source for rating in saved.external_ratings] == [
        "Internet Movie Database",
        "Rotten Tomatoes",
    ]
    assert [rating.normalized_score for rating in saved.external_ratings] == [
        87.0,
        73.0,
    ]


def test_save_movie_rolls_back_complete_transaction_on_rating_error(
    movie_repository: MovieRepository,
    conn: sqlite3.Connection,
    movie_factory: Callable[..., Movie],
) -> None:
    ratings = [
        ExternalRating(source="IMDb", value="8/10"),
        ExternalRating(source="IMDb", value="9/10"),
    ]
    movie = movie_factory(external_ratings=ratings)

    with pytest.raises(sqlite3.IntegrityError):
        movie_repository.save_movie(movie)

    assert conn.execute("SELECT COUNT(*) FROM media").fetchone() == (0,)
    assert conn.execute("SELECT COUNT(*) FROM movie_details").fetchone() == (0,)
    assert conn.execute("SELECT COUNT(*) FROM external_ratings").fetchone() == (0,)
    assert movie.id is None
    assert all(rating.id is None for rating in ratings)
    assert all(rating.media_id is None for rating in ratings)


def test_search_movie_is_case_insensitive_and_ignores_spaces(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory())

    result = movie_repository.search_data_movie("  INTERSTELLAR  ")

    assert result is not None
    assert result.title == "Interstellar"


def test_search_movie_returns_none_for_blank_or_missing_title(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.search_data_movie("   ") is None
    assert movie_repository.search_data_movie("Missing") is None


def test_search_movie_by_id_returns_none_when_missing(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.search_movie_by_id(999) is None


def test_search_movie_results_uses_partial_case_insensitive_match(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory())
    movie_repository.save_movie(
        movie_factory(
            title="The Internship",
            year=2013,
            imdb_id="tt2234155",
        )
    )
    movie_repository.save_movie(
        movie_factory(
            title="Arrival",
            year=2016,
            imdb_id="tt2543164",
        )
    )

    results = movie_repository.search_movie_results(" INTER ")

    assert [result.title for result in results] == [
        "Interstellar",
        "The Internship",
    ]
    assert all(result.local_id is not None for result in results)


def test_search_movie_results_returns_empty_for_blank_search(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.search_movie_results("   ") == []


def test_find_local_ids_by_imdb_ids_is_case_insensitive(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory())

    result = movie_repository.find_local_ids_by_imdb_ids(
        ["TT0816692", "tt9999999"]
    )

    assert result == {"tt0816692": 1}


def test_find_local_ids_by_imdb_ids_handles_empty_list(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.find_local_ids_by_imdb_ids([]) == {}


def test_list_movies_returns_movies_alphabetically(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory())
    movie_repository.save_movie(
        movie_factory(
            title="Arrival",
            year=2016,
            imdb_id="tt2543164",
        )
    )

    result = movie_repository.list_movies()

    assert [movie.title for movie in result] == ["Arrival", "Interstellar"]
    assert [movie.id for movie in result] == [2, 1]


def test_list_movies_returns_empty_list(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.list_movies() == []


def test_update_review_returns_true_and_changes_timestamp(
    movie_repository: MovieRepository,
    conn: sqlite3.Connection,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()
    movie_repository.save_movie(movie)
    conn.execute(
        "UPDATE media SET updated_at = '2000-01-01 00:00:00' WHERE id = ?",
        (movie.id,),
    )
    conn.commit()

    updated = movie_repository.update_review(5, movie.id)  # type: ignore[arg-type]
    saved = movie_repository.search_movie_by_id(movie.id)  # type: ignore[arg-type]

    assert updated is True
    assert saved is not None
    assert saved.avaliation == 5
    assert saved.updated_at is not None
    assert saved.updated_at > datetime(2000, 1, 1)


def test_update_review_returns_false_for_missing_movie(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.update_review(5, 999) is False


def test_update_comment_returns_true_and_saves_comment(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()
    movie_repository.save_movie(movie)

    updated = movie_repository.update_comment(
        "Excelente",
        movie.id,  # type: ignore[arg-type]
    )
    saved = movie_repository.search_movie_by_id(movie.id)  # type: ignore[arg-type]

    assert updated is True
    assert saved is not None
    assert saved.comment == "Excelente"


def test_update_comment_returns_false_for_missing_movie(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.update_comment("Excelente", 999) is False


def test_delete_movie_removes_related_rows(
    movie_repository: MovieRepository,
    conn: sqlite3.Connection,
    movie_factory: Callable[..., Movie],
) -> None:
    movie = movie_factory()
    movie_repository.save_movie(movie)

    deleted = movie_repository.delete_movie(movie.id)  # type: ignore[arg-type]

    assert deleted is True
    assert movie_repository.search_movie_by_id(movie.id) is None  # type: ignore[arg-type]
    assert conn.execute(
        "SELECT COUNT(*) FROM movie_details"
    ).fetchone() == (0,)
    assert conn.execute(
        "SELECT COUNT(*) FROM external_ratings"
    ).fetchone() == (0,)


def test_delete_movie_returns_false_when_missing(
    movie_repository: MovieRepository,
) -> None:
    assert movie_repository.delete_movie(999) is False


def test_duplicate_imdb_id_raises_integrity_error(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory())

    with pytest.raises(sqlite3.IntegrityError):
        movie_repository.save_movie(
            movie_factory(
                title="Different title",
                imdb_id="TT0816692",
            )
        )


def test_same_title_with_different_imdb_id_is_allowed(
    movie_repository: MovieRepository,
    movie_factory: Callable[..., Movie],
) -> None:
    movie_repository.save_movie(movie_factory())
    second = movie_factory(imdb_id="tt0000001")

    movie_repository.save_movie(second)

    assert second.id == 2
