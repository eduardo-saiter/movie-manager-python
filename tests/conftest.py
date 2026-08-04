from __future__ import annotations

import os
import sqlite3
from collections.abc import Callable, Iterator
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from clients.movie_api_client import MovieApiClient
from database.database import initialize_database
from models.movie import Movie
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices

# Garante que importar web_app não dependa do .env pessoal do desenvolvedor.
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
            "year": "2014",
            "genre": "Adventure, Drama, Sci-Fi",
            "director": "Christopher Nolan",
            "plot": "Exploradores atravessam um buraco de minhoca.",
            "poster": "https://example.com/interstellar.jpg",
            "comment": None,
            "id": None,
            "avaliation": 0,
        }
        data.update(overrides)
        return Movie(**data)  # type: ignore[arg-type]

    return factory


@pytest.fixture
def web_service_mock() -> Mock:
    return Mock(spec=MovieServices)


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    web_service_mock: Mock,
) -> Iterator[TestClient]:
    import routers.movie_router as movie_router
    from web_app import app

    monkeypatch.setattr(movie_router, "service", web_service_mock)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def close_web_database_connection() -> Iterator[None]:
    yield

    import sys

    web_dependencies = sys.modules.get("web_dependencies")
    if web_dependencies is not None:
        web_dependencies.conn.close()
