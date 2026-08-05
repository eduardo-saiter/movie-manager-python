import sqlite3

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse

from errors import MovieAlreadySavedError, MovieNotFoundError
from services.movie_services import MovieServices
from web_dependencies import get_movie_service, templates

router = APIRouter()

_DATABASE_ERROR_MESSAGE = "Não foi possível acessar o banco de dados."


@router.get("/", name="home")
def home(
    request: Request,
    service: MovieServices = Depends(get_movie_service),
):
    try:
        movies = service.list_saved_movies()
    except sqlite3.Error:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "Movie Manager",
                "movies": [],
                "error": _DATABASE_ERROR_MESSAGE,
            },
            status_code=503,
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Movie Manager",
            "movies": movies,
            "error": None,
        },
    )


@router.get("/search", name="search_movie_page")
def search_movie_page(
    request: Request,
    title: str = "",
    service: MovieServices = Depends(get_movie_service),
):
    try:
        results = service.search_results(title)
    except (ValueError, ConnectionError, sqlite3.Error) as error:
        if isinstance(error, sqlite3.Error):
            error_message = _DATABASE_ERROR_MESSAGE
            status_code = 503
        elif isinstance(error, ConnectionError):
            error_message = str(error)
            status_code = 503
        else:
            error_message = str(error)
            status_code = 400

        return templates.TemplateResponse(
            request=request,
            name="search_results.html",
            context={
                "page_title": "Resultados da pesquisa",
                "search": title,
                "results": [],
                "error": error_message,
            },
            status_code=status_code,
        )

    return templates.TemplateResponse(
        request=request,
        name="search_results.html",
        context={
            "page_title": "Resultados da pesquisa",
            "search": title,
            "results": results,
            "error": None,
        },
    )


@router.post("/movies/save", name="save_movie_page")
def save_movie_page(
    request: Request,
    imdb_id: str = Form(""),
    service: MovieServices = Depends(get_movie_service),
):
    try:
        movie = service.search_api_by_imdb_id(imdb_id)
        service.save_movie(movie)
    except (
        MovieAlreadySavedError,
        ValueError,
        ConnectionError,
        sqlite3.Error,
    ) as error:
        if isinstance(error, sqlite3.Error):
            error_message = _DATABASE_ERROR_MESSAGE
            status_code = 503
        elif isinstance(error, ConnectionError):
            error_message = str(error)
            status_code = 503
        elif isinstance(error, MovieAlreadySavedError):
            error_message = str(error)
            status_code = 409
        else:
            error_message = str(error)
            status_code = 400

        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": error_message,
            },
            status_code=status_code,
        )

    return RedirectResponse(
        url=str(
            request.app.url_path_for(
                "search_movie_id_page",
                movie_id=movie.id,
            )
        ),
        status_code=303,
    )


@router.post(
    "/movies/{movie_id}/update-rating",
    name="update_rating_page",
)
def update_rating_page(
    request: Request,
    movie_id: int,
    rating: str = Form(""),
    service: MovieServices = Depends(get_movie_service),
):
    try:
        service.new_review_movie(movie_id, rating)
    except MovieNotFoundError as error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Filme não encontrado",
                "movie": None,
                "error": str(error),
            },
            status_code=404,
        )
    except ValueError as error:
        try:
            movie = service.search_movie_by_id(movie_id)
        except sqlite3.Error:
            movie = None

        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": movie,
                "error": str(error),
            },
            status_code=400,
        )
    except sqlite3.Error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": _DATABASE_ERROR_MESSAGE,
            },
            status_code=503,
        )

    return RedirectResponse(
        url=str(
            request.app.url_path_for(
                "search_movie_id_page",
                movie_id=movie_id,
            )
        ),
        status_code=303,
    )


@router.post(
    "/movies/{movie_id}/update-comment",
    name="update_comment_page",
)
def update_comment_page(
    request: Request,
    movie_id: int,
    comment: str = Form(""),
    service: MovieServices = Depends(get_movie_service),
):
    try:
        service.new_comment_movie(movie_id, comment)
    except MovieNotFoundError as error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Filme não encontrado",
                "movie": None,
                "error": str(error),
            },
            status_code=404,
        )
    except ValueError as error:
        try:
            movie = service.search_movie_by_id(movie_id)
        except sqlite3.Error:
            movie = None

        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": movie,
                "error": str(error),
            },
            status_code=400,
        )
    except sqlite3.Error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": _DATABASE_ERROR_MESSAGE,
            },
            status_code=503,
        )

    return RedirectResponse(
        url=str(
            request.app.url_path_for(
                "search_movie_id_page",
                movie_id=movie_id,
            )
        ),
        status_code=303,
    )


@router.post(
    "/movies/{movie_id}/delete-movie",
    name="delete_movie_page",
)
def delete_movie_page(
    request: Request,
    movie_id: int,
    service: MovieServices = Depends(get_movie_service),
):
    try:
        service.delete_saved_movie(movie_id)
    except MovieNotFoundError as error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": str(error),
            },
            status_code=404,
        )
    except ValueError as error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": str(error),
            },
            status_code=400,
        )
    except sqlite3.Error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": _DATABASE_ERROR_MESSAGE,
            },
            status_code=503,
        )

    return RedirectResponse(
        url=str(request.app.url_path_for("home")),
        status_code=303,
    )


@router.get(
    "/movies/{movie_id}",
    name="search_movie_id_page",
)
def movie_details_page(
    request: Request,
    movie_id: int,
    service: MovieServices = Depends(get_movie_service),
):
    try:
        movie = service.search_movie_by_id(movie_id)
    except sqlite3.Error:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Detalhes do filme",
                "movie": None,
                "error": _DATABASE_ERROR_MESSAGE,
            },
            status_code=503,
        )

    if movie is None:
        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Filme não encontrado",
                "movie": None,
                "error": "O filme solicitado não foi encontrado.",
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        request=request,
        name="details_data.html",
        context={
            "movie": movie,
            "page_title": "Detalhes do filme",
            "error": None,
        },
    )


@router.get(
    "/omdb/{imdb_id}",
    name="omdb_details_page",
)
def omdb_details_page(
    request: Request,
    imdb_id: str,
    service: MovieServices = Depends(get_movie_service),
):
    try:
        movie = service.search_api_by_imdb_id(imdb_id)
    except (ValueError, ConnectionError) as error:
        status_code = 503 if isinstance(error, ConnectionError) else 404

        return templates.TemplateResponse(
            request=request,
            name="details_data.html",
            context={
                "page_title": "Filme não encontrado",
                "movie": None,
                "error": str(error),
            },
            status_code=status_code,
        )

    return templates.TemplateResponse(
        request=request,
        name="details_data.html",
        context={
            "page_title": "Detalhes do filme",
            "movie": movie,
            "error": None,
        },
    )
