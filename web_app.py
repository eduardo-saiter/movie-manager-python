from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from routers.movie_router import router as movie_router


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Movie Manager")

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

app.include_router(movie_router)