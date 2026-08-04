from collections.abc import Iterator
from pathlib import Path

from fastapi.templating import Jinja2Templates

from clients.movie_api_client import MovieApiClient
from database.database import connect, initialize_database
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

api_client = MovieApiClient()


def get_movie_service() -> Iterator[MovieServices]:
    conn = connect()

    initialize_database(conn)

    repository = MovieRepository(conn)

    service = MovieServices(
        api_client,
        repository,
    )

    try:
        yield service
    finally:
        conn.close()