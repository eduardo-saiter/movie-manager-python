import sqlite3
from unittest.mock import Mock

import pytest

from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices


@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")

    conn.execute(
        """
        CREATE TABLE movies (
            title TEXT NOT NULL COLLATE NOCASE,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            director TEXT NOT NULL,
            plot TEXT NOT NULL,
            comment TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliation INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    yield conn

    conn.close()


@pytest.fixture
def movie_repository(conn: sqlite3.Connection) -> MovieRepository:
    return MovieRepository(conn)


@pytest.fixture
def api_client_mock() -> Mock:
    return Mock(spec=MovieApiClient)


@pytest.fixture
def movie_repository_mock() -> Mock:
    repository = Mock(spec=MovieRepository)
    repository.search_data_movie.return_value = None
    return repository


@pytest.fixture
def movie_service(
    api_client_mock: Mock,
    movie_repository_mock: Mock,
) -> MovieServices:
    return MovieServices(api_client_mock, movie_repository_mock)
