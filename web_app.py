from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from services.movie_services import MovieServices
from clients.movie_api_client import MovieApiClient
from repositories.movies_repository import MovieRepository
from database.database import (
    connect,
    initialize_database
)


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Movie Manager")


app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

conn = connect()
initialize_database(conn)
api_client = MovieApiClient()
repository = MovieRepository(conn)
service = MovieServices(api_client, repository)


@app.get("/")
def home(request: Request):

    movies = service.list_saved_movies()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Movie Manager",
            "movies": movies,

        },
    )


@app.get("/search")
def search_movie_page(
    request: Request,
    title: str,
):
    try:
        movie = service.search_movie(title)

        if movie is None:
            movie = service.search_api(title)

        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Resultado da pesquisa",
                "movie": movie,
                "error": None,
            },
        )

    except ValueError as error:
        return templates.TemplateResponse(
            request=request,
            name="search_result.html",
            context={
                "page_title": "Resultado da pesquisa",
                "movie": None,
                "error": str(error),
            },
        )


@app.post("/movies/save")
def save_movie_page(
    title: str = Form(...),
):
    saved_movie = service.search_movie(title)

    if saved_movie is None:
        movie = service.search_api(title)
        service.save_movie(movie)

        query = urlencode({"title": title})

        return RedirectResponse(
            url=f"/search?{query}",
            status_code=303,
        )

@app.post("/movies/{movie_id}/update-rating")
def update_rating_page(
    movie_id: int,
    rating: int = Form(...),
    title: str = Form(...)
):
    service.new_review_movie(movie_id, rating)

    query = urlencode({"title": title})

    return RedirectResponse(
        url=f"/search?{query}",
        status_code=303,

    )


@app.post("/movies/{movie_id}/update-comment")
def update_comment_page(
    movie_id: int,
    comment: str = Form(...),
    title: str = Form(...)
):
    service.new_comment_movie(movie_id, comment)

    query = urlencode({"title": title})

    return RedirectResponse(
        url=f"/search?{query}",
        status_code=303,
    )


@app.post("/movies/{movie_id}/delete-movie", name="delete_movie_page")
def delete_movie_page(
    movie_id: int,
):
    service.delete_saved_movie(movie_id)

    return RedirectResponse(
        url="/",
        status_code=303,
    )

@app.get("/movies/{movie_id}", name="search_movie_id_page")
def movie_details_page(
    request: Request,
    movie_id: int,
):
    movie = service.search_movie_by_id(movie_id)

    stars = (
        "⭐" * movie.avaliation
        + "☆" * (5 - movie.avaliation))
    

    return templates.TemplateResponse(
        request=request,
        name="search_result.html",
        context={"movie": movie,"stars":str},
    )