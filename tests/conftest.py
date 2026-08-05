from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Iterator
from datetime import date
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from clients.movie_api_client import MovieApiClient
from database.database import initialize_database
from models.external_rating import ExternalRating
from models.media_search_result import MediaSearchResult
from models.movie import Movie
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices

os.environ.setdefault("OMDB_API_KEY", "test-api-key")


@pytest.fixture
def conn() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    initialize_database(connection)
    yield connection
    connection.close()


@pytest.fixture
def movie_repository(conn: sqlite3.Connection) -> MovieRepository:
    return MovieRepository(conn)


@pytest.fixture
def api_client_mock() -> Mock:
    return Mock(spec=MovieApiClient)


@pytest.fixture
def repository_mock() -> Mock:
    return Mock(spec=MovieRepository)


@pytest.fixture
def movie_service(
    api_client_mock: Mock,
    repository_mock: Mock,
) -> MovieServices:
    return MovieServices(api_client_mock, repository_mock)


@pytest.fixture
def movie_factory() -> Callable[..., Movie]:
    def factory(**overrides: object) -> Movie:
        data: dict[str, object] = {
            "title": "Interstellar",
            "year": 2014,
            "genre": "Adventure, Drama, Sci-Fi",
            "director": "Christopher Nolan",
            "plot": "Exploradores atravessam um buraco de minhoca.",
            "media_type": "movie",
            "imdb_id": "tt0816692",
            "poster": "https://example.com/interstellar.jpg",
            "awards": "1 Oscar",
            "runtime_minutes": 169,
            "released_at": date(2014, 11, 7),
            "imdb_rating": 8.7,
            "imdb_votes": 2_400_000,
            "metascore": 74,
            "box_office": 188_020_017,
            "comment": None,
            "id": None,
            "avaliation": 0,
            "external_ratings": [
                ExternalRating(
                    source="Internet Movie Database",
                    value="8.7/10",
                    normalized_score=87.0,
                ),
                ExternalRating(
                    source="Rotten Tomatoes",
                    value="73%",
                    normalized_score=73.0,
                ),
            ],
        }
        data.update(overrides)
        return Movie(**data)  # type: ignore[arg-type]

    return factory


@pytest.fixture
def search_result_factory() -> Callable[..., MediaSearchResult]:
    def factory(**overrides: object) -> MediaSearchResult:
        data: dict[str, object] = {
            "title": "Interstellar",
            "year": "2014",
            "media_type": "movie",
            "imdb_id": "tt0816692",
            "poster": "https://example.com/interstellar.jpg",
            "local_id": None,
        }
        data.update(overrides)
        return MediaSearchResult(**data)  # type: ignore[arg-type]

    return factory


@pytest.fixture
def web_service_mock() -> Mock:
    return Mock(spec=MovieServices)


@pytest.fixture
def client(
    web_service_mock: Mock,
) -> Iterator[TestClient]:
    from web_app import app
    from web_dependencies import get_movie_service

    app.dependency_overrides[get_movie_service] = lambda: web_service_mock

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
