from pathlib import Path

from fastapi.templating import Jinja2Templates

from clients.movie_api_client import MovieApiClient
from database.database import (connect,initialize_database)
from repositories.movies_repository import MovieRepository
from services.movie_services import MovieServices


BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

conn = connect()
initialize_database(conn)

repository = MovieRepository(conn)
api_client = MovieApiClient()

service = MovieServices(
    api_client,
    repository,
)